import argparse
import shutil
import spiakid_simulation as sm
import spiakid_simulation.PhotonSimulator as sim
import spiakid_simulation.image_process.PSF_interface as inter
import spiakid_simulation.new_version.SimPhoton as sim_2

def parse():

    parser = argparse.ArgumentParser(description='MKID phase simulation')
    parser.add_argument('--example', help='Copy examples in a non existant folder',dest='folder_path')
    parser.add_argument('--sim', help='Launch the simulation',dest = 'Yaml_path')
    parser.add_argument('--sim_new', help='Launch the simulation with the new version',dest = 'Yaml_path_new')
    parser.add_argument('--psf', help='Launch an interface to vizualise a PSF', dest='PSF_path')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse()

    if args.folder_path:
        p = sm.__path__[0]
        shutil.copytree(p+'/Example', args.folder_path, symlinks=False, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False, dirs_exist_ok=False)
    
    if args.Yaml_path:
        sim.PhotonSimulator(args.Yaml_path)

    if args.Yaml_path_new:
        sim_2.Simulation(args.Yaml_path_new)

    if args.PSF_path:
        inter.interface(args.PSF_path)