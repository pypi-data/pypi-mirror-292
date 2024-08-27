def add_analysis_parser(subparsers):
    # Input arguments:

    parser = subparsers.add_parser("analysis", help="Analysis of search results.")
    parser.set_defaults(func=cli_analysis)    

    parser.add_argument("-d", "--directories", nargs="+", type=str)  # List - Directories
    parser.add_argument("-dE", "--delta_energy", type=float, default=0.05)
    parser.add_argument("-DE", "--Delta_energy", type=float, default=None)
    parser.add_argument("--save_name", type=str, default=None)

    # Flags
    parser.add_argument("-c", "--plot_cdf", action="store_false")  # Bool - Plot CDF
    parser.add_argument("-s", "--plot_structure", action="store_false")  # Bool - Plot structure
    parser.add_argument("-e", "--plot_energies", action="store_true")  # Bool - Plot energy
    parser.add_argument("-hg", "--plot_histogram", action="store_false")  # Bool - Plot histogram
    parser.add_argument("-p", "--print_all", action="store_true")  # Print everything
    parser.add_argument("-v", "--view_best", action="store_true")
    parser.add_argument("-g", "--save", action="store_true")  # Save the figure?
    parser.add_argument("-sd", "--save_data", action="store_false")
    parser.add_argument("-fr", "--force_reload", action="store_true")

    # Histogram settings:
    parser.add_argument(
        "-hgl", "--histogram_limits", nargs="+", default=[0, 0]
    )  # Histogram limits: min iteration, max iteration
    parser.add_argument("-hgop", "--histogram_operation", type=str, default="best")  # Histogram operations: best, all
    parser.add_argument(
        "-hgth", "--histogram_threshold", type=int, default=1000
    )  # Histogram energy threshold: 0 gives all (negative) energies, positive number gives that over the best found.

    # Animation related things:
    parser.add_argument("-a", "--animate", action="store_false")  # Print everything

def cli_analysis(args):
    from agox.utils.batch_analysis import Analysis, KeyBoardEvent
    import matplotlib.pyplot as plt

    directories = args.directories

    if args.Delta_energy is None:
        dE = args.delta_energy
        delta_energy = None
    else:
        dE = None
        delta_energy = args.Delta_energy

    # Plots:
    plot_cdf = args.plot_cdf
    plot_structure = args.plot_structure
    plot_energies = args.plot_energies
    plot_histogram = args.plot_histogram
    num_plots = plot_cdf + plot_structure + plot_energies + plot_histogram
    print_all = args.print_all
    view_best = args.view_best

    histogram_kwargs = {
        "min_hist_iteration": int(args.histogram_limits[0]),
        "max_hist_iteration": int(args.histogram_limits[1]),
        "operation": args.histogram_operation,
        "threshold": args.histogram_threshold,
    }

    # Save/reload
    save_data = args.save_data
    force_reload = args.force_reload

    # Saving?
    save = args.save
    save_name = args.save_name

    animate = args.animate

    # Start
    A = Analysis(
        directories,
        dE=dE,
        save_data=save_data,
        force_reload=force_reload,
        histogram_kwargs=histogram_kwargs,
        delta_energy=delta_energy,
    )
    # A = Analysis(directories, dE=dE, save_data=True, force_reload=False)

    A.analyse_directories()
    A.calculate_CDF()

    A.print_info(print_all)

    # Open the best structure in the ASE GUI.
    if view_best:
        A.global_best_structure.edit()

    if num_plots > 0:
        fig, axes = plt.subplots(1, num_plots, figsize=(num_plots * 5, 5))
        if num_plots > 1:
            axes = axes.flatten()
        else:
            axes = [axes]

        ax_idx = 0
        if plot_structure:
            if animate:
                atoms_patch_collection, structures, energies = A.animate_structure(axes[ax_idx])
            else:
                A.plot_structure(axes[ax_idx], A.global_best_structure)

            struct_ax = axes[ax_idx]
            ax_idx += 1
        else:
            struct_ax = None

        if plot_cdf:
            A.plot_CDF(axes[ax_idx])
            cdf_ax = axes[ax_idx]
            ax_idx += 1
        else:
            cdf_ax = None

        if plot_energies:
            A.plot_energy(axes[ax_idx])
            energy_ax = axes[ax_idx]
            ax_idx += 1
        else:
            energy_ax = None

        if plot_histogram:
            A.plot_histogram(axes[ax_idx])
            hist_ax = axes[ax_idx]
            ax_idx += 1
        else:
            hist_ax = None

        if animate:
            if plot_structure:
                named_axes = [struct_ax, cdf_ax, energy_ax, hist_ax]
                callback = KeyBoardEvent(fig, atoms_patch_collection, structures, energies, named_axes=named_axes)
                fig.canvas.mpl_connect('key_press_event', callback.press)
            else:
                print("To use the animation, the structure has to be plotted")

        plt.tight_layout()

        if save:
            if save_name is None:
                save_name = directories[0]
            plt.savefig(
                os.path.join(save_name + strftime("%Y_%m_%d") + ".png"),
                bbox_inches="tight",
            )

        plt.show()
