# main.py
# Imports:

# Main functionality to interact with the data-base/sets, their shapes/information, and labels.
class MedShapeNet:
    '''
    This class holds the main methods to:
     - Access the database
     - Download datasets/medical shapes
     - Visualize shapes
     - Convert shapes file format for Machine Learning applications
     - Gain dataset's author and paper information
     - *Under construction, more to come*

    If this API was found useful within your research please cite MedShapeNet:
     @article{li2023medshapenet,
     title={MedShapeNet--A Large-Scale Dataset of 3D Medical Shapes for Computer Vision},
     author={Li, Jianning and Pepe, Antonio and Gsaxner, Christina and Luijten, Gijs and Jin, Yuan and Ambigapathy, Narmada and Nasca, Enrico and Solak, Naida and Melito, Gian Marco and Memon, Afaque R and others},
     journal={arXiv preprint arXiv:2308.16139},
     year={2023}
     }

    METHODS:
    --------
    msn_help() -> None
        Prints a help message about the package's current status.
    --------
    *Under construction*
    '''
    # Help method explaining all functions and a few examples.
    def msn_help(self) -> None:
        '''
        Prints a help message regarding current functionality of MedShapeNet API.
        
        Returns:
        --------
        None
        '''
        print("This package is currently under heavy construction, functionality will come soon!")
    
    # Second method


# Wrapper function(s) -> make them callable from CLI
def cli_msn_help() -> None:
    """
    Creates an instance of MedShapeNet and calls its msn_help method.
    
    Returns
    -------
    None
    """
    msn_instance = MedShapeNet()
    msn_instance.msn_help()

# Entry point for direct execution
if __name__ == "__main__":
    # Print the help statement directly
    print("Running MedShapeNet directly...")
    cli_msn_help()