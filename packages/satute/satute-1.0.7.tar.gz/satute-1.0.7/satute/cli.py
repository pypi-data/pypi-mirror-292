# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import numpy as np
import traceback

from pathlib import Path
from ete3 import Tree

from logging import Logger
from typing import Optional, Dict, List
from Bio.Align import MultipleSeqAlignment

from satute.logging_utils import (
    log_iqtree_run_and_satute_info,
    log_tested_tree,
    log_consider_iqtree_message,
    log_iqtree_options,
    setup_logging_configuration,
)

from satute.exceptions import ModelNotFoundError, InvalidModelNameError
from satute.spectral_decomposition import spectral_decomposition
from satute.partial_likelihood.rate_matrix import RateMatrix
from satute.handler.file_handler import FileHandler
from satute.handler.iqtree_handler import IqTreeHandler
from satute.trees import rename_internal_nodes_pre_order
from satute.arguments import ARGUMENT_LIST
from satute.satute_file.satute_file_writer import SatuteFileWriter
from satute.rate_analysis import multiple_rate_analysis, single_rate_analysis
from satute.models.substitution_model import SubstitutionModel

from satute.valid_data_input import (
    validate_category_range,
    validate_and_check_rate_categories,
    validate_and_set_rate_category,
    validate_satute_input_options,
)


from satute.ostream import (
    write_results_for_category_rates,
    write_alignment_and_indices,
    write_posterior_probabilities_single_rate,
    write_posterior_probabilities_for_rates,
    write_components,
)

from satute.categories import (
    read_alignment_file,
    split_msa_into_rate_categories_in_place,
    build_categories_by_sub_tables,
)

from satute.parser.iqtree_parser import (
    parse_substitution_model,
    parse_rate_from_cli_input,
    parse_file_to_data_frame,
    IqTreeParser,
)

from satute.messages.messages import SATUTE_VERSION
from importlib.metadata import version as get_version


class Satute:
    """Class representing Satute command-line tool for wrapping up functions of IQ-TREE."""

    def __init__(
        self,
        iqtree_executable: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        # IQ-TREE related attributes
        self.iqtree: Optional[str] = iqtree_executable
        self.iqtree_tree_file: Optional[Path] = None
        self.iqtree_handler: Optional[IqTreeHandler] = None

        # Directories and paths
        self.input_dir: Optional[Path] = None
        self.site_probabilities_file: Optional[Path] = None
        self.active_directory: Optional[Path] = None
        self.file_writer: Optional[SatuteFileWriter] = None
        self.alpha: float = 0.05
        self.categorized_sites = None

        # Miscellaneous attributes
        self.output_prefix: Optional[str] = None
        self.input_args: List[argparse.Namespace] = []
        self.number_rates: int = 1
        self.logger: Optional[Logger] = logger
        self.iqtree_arguments: Dict[str, List[str]] = {}
        self.results = None
        self.alignment = None

    def configure(self):
        # Method to parse and validate command line arguments, initialize directory and handlers
        self.initialize_active_directory()
        self.initialize_handlers()

    def parse_command_line_input(self, args=None):
        """
        Parse command-line arguments using the argparse module. It dynamically
        adds arguments to the parser based on a predefined list of argument
        configurations, ensuring flexibility and ease of updates.
        """
        parser = argparse.ArgumentParser(description="SatuTe", exit_on_error=True)

        # Automatically fetch the version from package metadata
        package_version = get_version("satute")

        # Add version argument
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"SatuTe {package_version}",
            help="Show the program's version and exit.",
        )

        for argument in ARGUMENT_LIST:
            # Unpack the dictionary directly without modifying the original list
            parser.add_argument(
                argument["flag"], **{k: v for k, v in argument.items() if k != "flag"}
            )

        self.input_args = parser.parse_args(args)
        validate_satute_input_options(self.input_args)

    def initialize_handlers(self):
        self.file_handler = FileHandler(self.active_directory)
        self.iqtree_handler = IqTreeHandler(self.input_args.iqtree, self.logger)

    def initialize_active_directory(self):
        if self.input_args.msa:
            self.active_directory = self.input_args.msa.parent
        elif self.input_args.dir:
            self.active_directory = self.input_args.dir

    def handle_number_rates(self):
        self.number_rates = 1
        if self.input_args.model:
            self.number_rates = parse_rate_from_cli_input(self.input_args.model)
        return self.number_rates

    def run_iqtree_workflow(self, arguments_dict: Dict[str, List]) -> None:
        extra_arguments: List[str] = []

        # Set number_rates once at the beginning
        self.handle_number_rates()

        if self.input_args.add_iqtree_options:
            extra_arguments.append(self.input_args.add_iqtree_options)
        if arguments_dict["option"] == "dir":
            self.logger.info(
                "IQ-TREE will not to be needed the analysis will be done on the already existing iqtree files."
            )
        else:
            # For the other options IQ-Tree is necessary. Therefore, test if IQ-TREE exists
            self.iqtree_handler.check_iqtree_path(self.input_args.iqtree)

        if arguments_dict["option"] == "dir + site_probabilities":
            self.logger.info("Running Satute with site probabilities")
            self.logger.info(
                "IQ-TREE will be needed for the site probabilities for the corresponding rate categories."
            )

            extra_arguments = extra_arguments + [
                "-m",
                self.input_args.model,
                "--redo",
                "-wspr",
                "--quiet",
                "--keep-ident",
            ]

            self.iqtree_handler.run_iqtree_with_arguments(
                arguments_dict["arguments"], extra_arguments
            )

        if arguments_dict["option"] == "msa":
            log_consider_iqtree_message(self.logger)
            self.logger.info(
                "If no model is specified in input arguments, best-fit model will be extracted from log file."
            )

            model_finder_arguments = [
                "-m MF",
                "--quiet",
                "--redo"
            ]

            (
                self.iqtree_handler.run_iqtree_with_arguments(
                    arguments=arguments_dict["arguments"],
                    extra_arguments=model_finder_arguments,
                ),
            )

            # Update model in input arguments and re-construct arguments
            iqtree_parser = IqTreeParser(f"{arguments_dict['msa_file']}.iqtree")

            self.input_args.model = iqtree_parser.parse_substitution_model()

            # Validate and append ufboot and boot parameters to extra_arguments
            bb_arguments = self.iqtree_handler.validate_and_append_boot_arguments(
                self.input_args.ufboot, self.input_args.boot
            )

            extra_arguments = bb_arguments + [
                "-m",
                self.input_args.model,
                "--redo",
                "--keep-ident",
                "--quiet",
            ]

            self.handle_number_rates()

            if self.number_rates > 1:
                extra_arguments = extra_arguments + ["-wspr"]

            self.iqtree_handler.run_iqtree_with_arguments(
                arguments=arguments_dict["arguments"], extra_arguments=extra_arguments
            )

        if arguments_dict["option"] == "msa + model":
            log_consider_iqtree_message(self.logger)

            bb_arguments = self.iqtree_handler.validate_and_append_boot_arguments(
                self.input_args.ufboot, self.input_args.boot
            )

            extra_arguments = bb_arguments + [
                "-m",
                self.input_args.model,
                "--quiet",
                "--keep-ident",
                "--redo",
            ]

            self.add_wspr_option_if_needed(extra_arguments=extra_arguments)

            self.iqtree_handler.run_iqtree_with_arguments(
                arguments=arguments_dict["arguments"], extra_arguments=extra_arguments
            )

        if arguments_dict["option"] == "msa + tree + model":
            log_consider_iqtree_message(self.logger)

            extra_arguments = extra_arguments + [
                "-m",
                self.input_args.model,
                "--quiet",
                "--keep-ident",
                '--redo'
            ]

            self.add_wspr_option_if_needed(extra_arguments=extra_arguments)

            # Call IQ-TREE with the constructed arguments
            self.iqtree_handler.run_iqtree_with_arguments(
                arguments_dict["arguments"], extra_arguments
            )

            log_iqtree_options(
                arguments_dict, extra_arguments=extra_arguments, logger=self.logger
            )

    def run(self):
        """
        Main entry point for running the Satute command-line tool.
        """
        try:
            # ======== Arguments =================
            msa_file: Path = self.input_args.msa

            # ======== Tree File Handling ========
            newick_string: str = self.file_handler.get_newick_string_from_iqtree_file(
                msa_file.resolve()
            )

            test_tree: Tree = rename_internal_nodes_pre_order(
                Tree(newick_string, format=1)
            )
            # ======== Model parameter ===========

            iqtree_file_path: str = f"{msa_file.resolve()}.iqtree"

            satute_iqtree_parser: IqTreeParser = IqTreeParser(iqtree_file_path)

            substitution_model: SubstitutionModel = (
                satute_iqtree_parser.load_substitution_model()
            )

            ## Convert representation of rate_matrix
            RATE_MATRIX = RateMatrix(substitution_model.rate_matrix)

            # Calculation of the spectral decomposition of the rate matrix
            (
                _,
                array_right_eigenvectors,
                multiplicity,
                eigenvalue,
            ) = spectral_decomposition(
                substitution_model.rate_matrix, substitution_model.phi_matrix
            )

            # Get number of rate categories in case of a +G or +R model
            validate_category_range(
                input_args=self.input_args, number_rates=self.number_rates
            )

            rate_category = "all"

            if self.input_args.category:
                rate_category = validate_and_set_rate_category(
                    input_category=self.input_args.category,
                    number_rates=substitution_model.number_rates,
                    logger=self.logger,
                )

            if self.number_rates == "AMBIGUOUS":
                self.number_rates = substitution_model.number_rates

            # ======== Multiple Sequence Alignment
            self.alignment: MultipleSeqAlignment = read_alignment_file(
                msa_file.resolve()
            )
            # ========  Test for Branch Saturation =========

            log_iqtree_run_and_satute_info(
                active_directory=self.active_directory,
                msa_file=Path(msa_file),
                iq_tree_arguments=self.iqtree_arguments,
                logger=self.logger,
            )

            log_tested_tree(
                self.logger, test_tree, option=self.iqtree_arguments["option"]
            )

            if substitution_model.number_rates == 1:
                self.run_single_rate_analysis(
                    test_tree,
                    self.alignment,
                    RATE_MATRIX,
                    substitution_model.state_frequencies,
                    array_right_eigenvectors,
                    multiplicity,
                    msa_file,
                    self.input_args.alpha,
                    self.input_args.edge,
                )

            else:
                self.run_multiple_rate_analysis(
                    test_tree,
                    substitution_model.category_rates,
                    RATE_MATRIX,
                    substitution_model.state_frequencies,
                    array_right_eigenvectors,
                    multiplicity,
                    self.alignment,
                    f"{msa_file.resolve()}.siteprob",
                    rate_category,
                    msa_file,
                    self.input_args.alpha,
                    self.input_args.edge,
                )

            self.write_satute_file(
                msa_file=msa_file,
                iq_tree_file=iqtree_file_path,
                test_tree=test_tree,
                rate_category=rate_category,
                substitution_model=substitution_model,
                multiplicity=multiplicity,
                eigenvalue=eigenvalue,
                array_right_eigenvectors=array_right_eigenvectors,
            )

        except (ModelNotFoundError, InvalidModelNameError, Exception) as e:
            traceback.print_exc()  # Print stack trace
            self.logger.error(f"An error occurred: {e}")
            sys.exit(1)

    def run_single_rate_analysis(
        self,
        test_tree: Tree,
        alignment: MultipleSeqAlignment,
        rate_matrix: RateMatrix,
        state_frequencies: List[float],
        array_right_eigenvectors: List[np.array],
        multiplicity: int,
        msa_file: Path,
        alpha: float,
        focused_edge: str,
    ):
        self.results = single_rate_analysis(
            test_tree,
            alignment,
            rate_matrix,
            state_frequencies,
            array_right_eigenvectors,
            multiplicity,
            alpha,
            focused_edge,
        )

        single_rate_indices: List[int] = [
            i for i in range(1, alignment.get_alignment_length() + 1, 1)
        ]

        single_rate_category = {"single_rate": single_rate_indices}

        write_results_for_category_rates(
            self.results,
            self.input_args.output_suffix,
            msa_file,
            self.input_args.alpha,
            self.input_args.edge,
            single_rate_category,
            self.logger,
        )

        if self.input_args.asr:
            self.logger.info(
                f"Writing ancestral sequences of the nodes on the left side and the right side of the branch. {self.active_directory.name}"
            )

            write_posterior_probabilities_single_rate(
                self.results,
                state_frequencies,
                msa_file,
                self.input_args.output_suffix,
                self.input_args.alpha,
                self.input_args.edge,
                alignment.get_alignment_length(),
            )

        write_components(
            self.results["single_rate"]["components"],
            msa_file,
            self.input_args.output_suffix,
            "single_rate",
            self.input_args.alpha,
            self.input_args.edge,
            single_rate_indices,
        )

    def run_multiple_rate_analysis(
        self,
        test_tree: Tree,
        category_rates: Dict[str, Dict],
        rate_matrix: RateMatrix,
        state_frequencies: List[float],
        array_right_eigenvectors: List[np.array],
        multiplicity: int,
        alignment: MultipleSeqAlignment,
        site_probability_file: str,
        rate_category: str,
        msa_file: Path,
        alpha: float = 0.05,
        edge: str = None,
    ):
        """
        Run the multiple rate analysis.
        """
        site_probability = parse_file_to_data_frame(site_probability_file)

        per_rate_category_alignment = split_msa_into_rate_categories_in_place(
            site_probability, alignment, rate_category
        )

        self.categorized_sites = build_categories_by_sub_tables(site_probability)

        self.results = multiple_rate_analysis(
            test_tree,
            category_rates,
            rate_matrix,
            state_frequencies,
            array_right_eigenvectors,
            multiplicity,
            per_rate_category_alignment,
            alpha,
            edge,
        )

        write_results_for_category_rates(
            self.results,
            self.input_args.output_suffix,
            msa_file,
            alpha,
            edge,
            self.categorized_sites,
            self.logger,
        )

        validate_and_check_rate_categories(
            self.categorized_sites, self.input_args.category, self.logger
        )

        if self.input_args.asr:
            self.logger.info(
                f"Writing ancestral sequences to {self.active_directory.name}"
            )

            write_posterior_probabilities_for_rates(
                self.results,
                state_frequencies,
                msa_file,
                self.input_args.output_suffix,
                self.input_args.alpha,
                self.input_args.edge,
                self.categorized_sites,
            )

        if self.input_args.category_assignment:
            write_alignment_and_indices(
                per_rate_category_alignment,
                self.categorized_sites,
                msa_file,
                logger=self.logger,
            )

        for rate, results_set in self.results.items():
            write_components(
                results_set["components"],
                msa_file,
                self.input_args.output_suffix,
                rate,
                self.input_args.alpha,
                self.input_args.edge,
                self.categorized_sites[rate],
            )

    def write_satute_file(
        self,
        msa_file: Path,
        iq_tree_file: Path,
        test_tree: Tree,
        rate_category: int,
        substitution_model: SubstitutionModel,
        multiplicity: int,
        eigenvalue: float,
        array_right_eigenvectors: List[np.array],
    ):
        if self.input_args.edge:
            self.file_writer = SatuteFileWriter(
                f"{msa_file.resolve()}_{self.input_args.alpha}_{self.input_args.edge}.satute"
            )
        else:
            self.file_writer = SatuteFileWriter(
                f"{msa_file.resolve()}_{self.input_args.alpha}.satute"
            )

        self.file_writer.open_file()

        self.file_writer.write_satute_file(
            msa_file,
            iq_tree_file,
            test_tree,
            rate_category,
            substitution_model,
            multiplicity,
            eigenvalue,
            array_right_eigenvectors,
            self.iqtree_arguments,
            categorized_sites=self.categorized_sites,
            input_args=self.input_args,
            alignment_length=self.alignment.get_alignment_length(),
            alpha=self.input_args.alpha,
            results=self.results,
        )

        self.file_writer.close_file()

    """BEGIN Input Argument Construction"""

    def get_dir_argument_options(self, msa_file: Path, tree_file: str):
        argument_option = {
            "option": "dir",
            "msa_file": Path(msa_file),
            "arguments": ["-s", str(Path(msa_file).resolve())],
        }

        if tree_file:
            argument_option["arguments"].extend(["-te", str(tree_file)])
        return argument_option

    def construct_iqtree_arguments(self):
        """
        Validate and process input arguments.

        Raises:
            InvalidDirectoryError: If the input directory does not exist.
            NoAlignmentFileError: If no multiple sequence alignment file is found.

        Returns:
            A dictionary with keys 'option', 'msa_file', and 'arguments' that represents the argument options for the process.
        """
        # Define the acceptable file types for sequence alignments and trees
        argument_option = {}
        if self.input_args.dir:
            self.input_args.msa = Path(self.file_handler.find_msa_file())
            self.iqtree_tree_file = self.file_handler.find_iqtree_file()
            substitution_model = parse_substitution_model(self.iqtree_tree_file)
            self.input_args.model = substitution_model
            self.handle_number_rates()

            # Check for site probabilities file
            if self.number_rates > 1:
                self.site_probabilities_file = self.file_handler.find_file_by_suffix(
                    {".siteprob"}
                )

                if not self.site_probabilities_file:
                    self.logger.error(
                        "For the inference of tree a model with rate categories has been specified. But no site probabilities file found in directory. Please rerun iqtree with the option -wspr"
                    )
                    sys.exit(1)

            return self.get_dir_argument_options(self.input_args.msa, None)
        else:
            argument_option = {}
            if self.input_args.msa:
                self.construct_arguments_for_msa(argument_option)
            if self.input_args.tree:
                self.construct_argument_for_tree(argument_option)
            # If a model was specified in the input arguments, add it to the argument options
            if self.input_args.model:
                self.construct_argument_for_model(argument_option)
        # Return the constructed argument options
        return argument_option

    def construct_arguments_for_msa(self, argument_option: Dict):
        """
        Constructs the arguments required for multiple sequence alignment (MSA).

        Args:
        argument_option (dict): The dictionary where MSA arguments are to be added.

        Returns:
        dict: Updated dictionary with MSA specific arguments.
        """
        # Specify the option type and MSA file path
        argument_option["option"] = "msa"
        argument_option["msa_file"] = self.input_args.msa
        # Add MSA specific command-line arguments
        argument_option["arguments"] = ["-s", str(self.input_args.msa.resolve())]
        return argument_option

    def construct_argument_for_tree(self, argument_option: Dict):
        """
        Appends tree-related arguments to the existing argument option.

        Args:
        argument_option (dict): The dictionary to which tree arguments are added.
        """
        # Specify that the option now includes tree data
        argument_option["option"] = "msa + tree"

        # Extend the existing arguments with tree specific command-line arguments
        argument_option["arguments"].extend(
            ["-te", str(self.input_args.tree.resolve())]
        )

    def construct_argument_for_model(self, argument_option: Dict):
        """
        Constructs the arguments required for the evolutionary model.

        Args:
        argument_option (dict): The dictionary where model arguments are to be added.
        """
        # Update the option to indicate inclusion of the model
        argument_option["option"] += " + model"

        # Add model specific command-line arguments
        argument_option["model_arguments"] = ["-m", self.input_args.model]

        # Add extra arguments if the model includes certain features
        if "+G" in self.input_args.model or "+R" in self.input_args.model:
            argument_option["model_arguments"].extend(["-wspr"])

    def add_wspr_option_if_needed(self, extra_arguments: List[str]) -> None:
        """
        Adds the '-wspr' option to the extra_arguments list if needed based on the number of rates.

        Args:
            extra_arguments (List[str]): List of additional arguments for IQ-TREE.

        Returns:
            None
        """
        if (
            (isinstance(self.number_rates, int) and self.number_rates > 1)
            or isinstance(self.number_rates, str)
            and self.number_rates == "AMBIGUOUS"
        ):
            extra_arguments.append("-wspr")

    """END Input Argument Construction"""


def main(args=None):
    # Instantiate the Satute class
    logger = logging.getLogger(__name__)
    satute = Satute(iqtree_executable="iqtree", logger=logger)

    try:
        # Parse and validate input arguments
        satute.parse_command_line_input(args)

        # Initialize file handler and logger
        satute.configure()

        setup_logging_configuration(
            logger=satute.logger,
            input_args=satute.input_args,
            msa_file=Path(satute.file_handler.find_msa_file()),
        )

        # IQ-Tree run if necessary
        satute.iqtree_arguments = satute.construct_iqtree_arguments()
        satute.logger.info(f"{SATUTE_VERSION}")

        try:
            satute.run_iqtree_workflow(satute.iqtree_arguments)
        except RuntimeError as e:
            logger.error(f"IQ-TREE error: {e}")
            if satute.input_args.dev:
                traceback.print_exc()  # Print stack trace
            sys.exit(1)
        satute.run()
    except (argparse.ArgumentTypeError, ModelNotFoundError, InvalidModelNameError) as e:
        # Argparse will print the error itself, no need to log it again
        logger.error(f"An error occurred: {e}")
        if satute.input_args.dev:
            traceback.print_exc()  # Print stack trace
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if satute.input_args.dev:
            traceback.print_exc()  # Print stack trace
        sys.exit(1)
    return 0


def cli():
    exit_code = main()
    sys.exit(exit_code)
