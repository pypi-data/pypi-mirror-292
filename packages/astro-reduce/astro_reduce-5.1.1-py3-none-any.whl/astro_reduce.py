'''astro_reduce -- A simple CCD-image reducer for the ObsPM.'''


from collections import defaultdict
from datetime import timedelta
from glob import glob
from json import loads, decoder
from os.path import basename, exists, getsize, splitext
from os import mkdir, getcwd, remove, system
from pkg_resources import resource_filename
from re import compile, sub
from shutil import copy, rmtree
from sys import exit
from time import time
from pathlib import Path
import importlib.util
import os

import click
import numpy as np
from matplotlib import pyplot as plt
from astropy.io import fits
from astropy.io.votable import parse
from astropy.table import Table
from astroquery.astrometry_net import AstrometryNet
from astropy.coordinates import SkyCoord
import astropy.units as u

from cosmetic import align_and_median
from helpers import write_png, fname_bits, write_conf_file, obj_read_header
from helpers import init_astro_header
from helpers import flat_read_header, dark_read_header
from helpers import OPT_LIST, ASTROMATIC_LIST, ASTROMETRYNET_LIST
from helpers import HC, UDARK, UFLAT, UOBJ
from helpers import DARK, FLAT, OBJ, TMP, MASTER
from helpers import DI, FI, RED, STK, AUX
from helpers import SEX_RES, PSFEX_RES, SCAMP_RES, AR, DATA
from helpers import T120_SEX, T120_PARAM, T120_PSFEX, T120_PARAMPSFEX
from helpers import DEFAULT_CONV, T120_SCAMP, T120_AHEAD
from helpers import SEX_CMD, PSFEX_CMD, SEXAGAIN_OPT_CMD, SCAMP_CMD
from helpers import SEX_NET, ASTRONET_CMD, ASTRONET_CFG, ASTRONET_DIR
from helpers import STRNB_MIN

@click.command()
@click.version_option()
@click.option('--setup', '-s', is_flag=True,
              help='Set up the directory for reduction. Use this option the '
              'first time astro_reduce is run in the directory or after the '
              '`--clear` option was used.')
@click.option('--clear', '-c', is_flag=True,
              help='Remove all astro_reduce-related files and folders in '
              'current directory , except the reduced images, and exit.')
@click.option('--clearall', '-z', is_flag=True,
              help='Remove all astro_reduce-related files and folders in '
              'current directory, including the reduced images, and exit.')
@click.option('--interpolate', '-i', is_flag=True,
              help='Interpolate existing dark fields if some are missing.')
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode (recommended).')
@click.option('--tmppng', '-t', is_flag=True,
              help='Write PNG format of auxiliary and master images '
              'after cosmetic reduction.')
@click.option('--stkpng', '-r', is_flag=True,
              help='Write PNG format of stacked images after cosmetic '
              'reduction.')
@click.option('--sex', is_flag=True,
              help='Run the `sex` astromatic command on all auxiliary images '
              'after the cosmetic reduction.')
@click.option('--psfex', is_flag=True,
              help='Run the `psfex` astromatic command with the '
              '`sex`-determined sources in all auxiliary images.')
@click.option('--sexagain', is_flag=True,
              help='Run the `sex` astromatic command a second time, using the '
              '`psfex`-determined PSF data.')
@click.option('--scamp', is_flag=True,
              help='Run the `scamp` astromatic command on all auxiliary images '
              'after cosmetic reduction.')
@click.option('-m','--astromatic', is_flag=True,
              help='Run the astromatic tools to solve the '
              'astrometry (sextractor, psfex, scamp).')
@click.option('-nl','--astrometrynet_local', is_flag=True,
              help='Run localy the solve-field script from astrometry.net to '
              'solve the astrometry. See also the --astrometrynet_online option.')
@click.option('-no','--astrometrynet_online', is_flag=True,
              help='Run the astropyquery.astrometry_net tool to solve the '
              'astrometry. See also the --astrometrynet_local option.')
@click.option('--nomaster', is_flag=True,
              help='If set, do not calculate the master darks and flats (and '
              'assume they are already there!). Useful for debug purpose.')
@click.option('--nostack', is_flag=True,
              help='If set, skip the stacking process.')
@click.option('--forceimg', is_flag=True,
              help='If set along with -n option, forces astrometry.net to use the whole image.')
@click.option('--astrometryonly', is_flag=True,
              help='If set only astrometry is performed. Useful for debug purpose.')

def cli(setup, clear, clearall, interpolate, verbose, tmppng, stkpng,
        sex, psfex, sexagain, scamp, astromatic, astrometrynet_local,
        astrometrynet_online, nomaster, 
        nostack, forceimg, astrometryonly):
    '''Main run of astro_reduce:

    If `--setup` option is on: copy all user fits data to files with standard
       names in the working directories, and exit.

    If `--clear` option is on: clear directory of all astro_reduce working data
    and exit.

    Else, cosmetic reduction procedure:
    i) Reduce dark field images to master darks for all exposures.
    ii) If necessary, interpolate darks for exposures lacking dark fields.
    iii) Reduce all flat field images to master transmission files.
    iv) Reduce all object images with the master reduction files.
    v) Stack the object images of same series.

    If `--{tmp,stk}png` options are on: generate PNG versions of auxiliary,
    master and stacked images.

    If `--{sex,psfex,sexagain,scamp}` options are on: run the astromatic suite
    on the auxiliary images to perform the astrometric reduction.

    '''
    # get astro_reduce installation directory
    package_name = 'astro_reduce'
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        package_path = spec.origin  
        package_dir = os.path.dirname(package_path) +'/'
    
    # Current working directory.
    cwd = basename(getcwd())

    # Welcome.
    click.secho('    Welcome to astro_reduce!\n'
                '    Software is copyright 2018-2022 Raphaël Duque & Jeremie Vaubaillon.\n\n',
                fg='cyan', bold=True)
    click.secho('Currently working in directory `{}`.'.format(cwd), fg='green')
    click.secho('Options: {}.'.format(', '.join(filter(eval, OPT_LIST))),
                fg='green')

    # Initialize configuration file name and timer.
    conf_file_name = '{}.json'.format(cwd)
    t0 = time()
    # This will hold the mapping between original and auxiliary files.
    u2ar = dict()

    # If clearALL option is on, remove all files and folders and exit.
    if clearall:
        clear = True
        click.secho('Clearing reduced and stacked images of astro_reduce files and folders...',
                    fg='green', nl=False)
        for folder in [RED, STK]:
            if exists(folder):
                rmtree(folder, ignore_errors=True)
    if clear:
        click.secho('Clearing directory of astro_reduce files and folders...',
                    fg='green', nl=False)
        if exists(conf_file_name):
            remove(conf_file_name)
        for folder in [OBJ, MASTER, DARK, FLAT, TMP, SEX_RES, PSFEX_RES,
                       SCAMP_RES]:
            if exists(folder):
                rmtree(folder, ignore_errors=True)
        click.secho(' Done.', fg='green')
        exit(0)

    # If setup option is on, set up the directory for reduction.
    if setup:
        verbose = True
        click.secho('Setting up for reduction:', fg='green')
        # Make sure the user image folders are there:
        if not (exists(UOBJ) and exists(UFLAT) and exists(UDARK)):
            click.secho('E: Did not find folder `DARK`, `FLAT` or `ORIGINAL`\n'
                        'E: containing the raw images to be reduced.\n'
                        'E: Refer to the documentation for details.', fg='red')
            exit(1)

        # Initialize objects, exposure, filters lists, and working directories.
        objects = list()
        exposures = list()
        filters = list()
        for folder in [OBJ, DARK, FLAT]:
            if exists(folder):
                rmtree(folder, ignore_errors=True)
            mkdir(folder)

        # Open all images, retrieve exposures, filters, etc. and copy files to
        # astro_reduce working directories. This way the images are backed-up
        # at the same time.
        if verbose:
            click.secho('  Copying dark field images...', nl=False)
        for file in glob('{}/*.fit*'.format(UDARK)):
            exp, fn = dark_read_header(file)
            exposures.append(exp)
            copy(file, '{}/{}'.format(DARK, fn))
        if verbose:
            click.secho('     Done.')

        if verbose:
            click.echo('  Copying flat field images...', nl=False)
        for file in glob('{}/*.fit*'.format(UFLAT)):
            fil, exp, fn = flat_read_header(file)
            exposures.append(exp)
            filters.append(fil)
            copy(file, '{}/{}'.format(FLAT, fn))
        if verbose:
            click.echo('     Done.')

        if verbose:
            click.echo('  Copying object images...', nl=False)
        for file in glob('{}/*.fit*'.format(UOBJ)):
            obj, fil, exp, fn = obj_read_header(file)
            objects.append(obj)
            filters.append(fil)
            exposures.append(exp)
            copy(file, '{}/{}'.format(OBJ, fn))
        if verbose:
            click.echo('         Done.')

        # Finish the setup by writing the configuration file.
        if verbose:
            click.echo('  Writing configuration file `{}`.'.format(
                                                                conf_file_name))
        write_conf_file(list(set(objects)), list(set(exposures)),
                        list(set(filters)), conf_file_name)

        click.secho('Done.', fg='green')
        exit(0)

    # Parse configuration file to obtain configuration dictionary.
    try:
        click.secho('Parsing configuration file `{}`.'.format(conf_file_name),
                    fg='green')
        with open(conf_file_name, 'r') as cfile:
            conf_dic = loads(cfile.read())
    except FileNotFoundError:
        click.secho('E: Configuration file `{}` not found.\n'
                    'E: If it is the first time you run astro_reduce in this\n'
                    'E: directory, use the --setup option to setup the\n'
                    'E: reduction and generate a configuration file.'
                    ''.format(conf_file_name), fg='red')
        exit(1)
    except decoder.JSONDecodeError:
        click.secho('E: Unable to parse configuration file `{}`.\n'
                    'E: Fix by rerunning astro_reduce with the --setup option.'
                    ''.format(conf_file_name), fg='red')
        exit(1)

    # Obtain list of all object, dark, flat field file names.
    object_files = dict(
        [(obj, glob('{}/{}_*.fit*'.format(OBJ, obj)))
            for obj in conf_dic['objects']])
    dark_files = dict(
        [(exp, glob('{}/{}_{}_*.fit*'.format(DARK, DI, exp)))
            for exp in conf_dic['exposures']])
    flat_files = dict(
        [(filt, glob('{}/{}_{}_*.fit*'.format(FLAT, FI, filt)))
            for filt in conf_dic['filters']])

    # Work out mapping between original and auxiliary files.
    for file in glob('{}/*.fit*'.format(UOBJ)):
        obj, fil, exp, fn = obj_read_header(file)
        nname = '{}'.format(fn.split('.fit')[0])
        u2ar[nname] = basename(file)

    # Check working directories are still there.
    if not (exists(OBJ) and exists(FLAT) and exists(DARK)):
        click.secho('E: Seems like astro_reduce\'s working folders\n'
                    'E: (those starting with `ar_`) were removed.\n'
                    'E: Please rerun astro_reduce with the --setup option.',
                    fg='red')
        exit(1)

    # Check all images are same size (if not we'll have a problem).
    listall = glob('{}/*'.format(DARK))\
                   + glob('{}/*'.format(FLAT))\
                   + glob('{}/*'.format(OBJ))
    hdr0 = fits.getheader(listall[0])
    (sz_x0,sz_y0) = (hdr0['NAXIS1'],hdr0['NAXIS2'])
    for fitsf in listall:
        hdr = fits.getheader(fitsf)
        (sz_x,sz_y) = (hdr['NAXIS1'],hdr['NAXIS2'])
        if not ((sz_x0,sz_y0)==(sz_x,sz_y)):
            click.secho('E: Seems like all image files don\'t have the same size.\n'
                        'E: Please remove offending files and rerun astro_reduce\n'
                        'E: with the --setup option.', fg='red')
            exit(1)     
#    if len(set(map(getsize,
#                   glob('{}/*'.format(DARK))
#                   + glob('{}/*'.format(FLAT))
#                   + glob('{}/*'.format(OBJ))))) != 1:
#        click.secho('E: Seems like all image files don\'t have the same size.\n'
#                    'E: Please remove offending files and rerun astro_reduce\n'
#                    'E: with the --setup option.', fg='red')
#        exit(1)

    # Check if files exist.
    for key in object_files:
        if not object_files[key]:
            click.secho('E: Did not find files for {} object.'.format(key),
                        fg='red')
            exit(1)
    for key in dark_files:
        if not dark_files[key] and not interpolate and not nomaster:
            # If the interpolate and nomaster options are off and there are some
            # darks missing, exit.
            click.secho('E: Did not find dark field images for {}ms exposure.\n'
                        'E: In order to interpolate the missing dark fields\n'
                        'E: from the ones available, rerun using the\n'
                        'E: --interpolate option.'.format(key), fg='red')
            exit(1)
    for key in flat_files:
        if not flat_files[key] and not nomaster:
            click.secho('E: No flat field images for {} filter.'.format(key),
                        fg='red')
            exit(1)

    # Report all files found.
    reg = compile(r'_[a-z0-9]*\.')
    if verbose:
        handy = lambda x: reg.sub('_*.', basename(x))
        click.secho('Files found:', fg='green')
        click.secho('  Objects (`{}`):'.format(OBJ), fg='blue')
        for obj in conf_dic['objects']:
            uniq_names = set(map(handy, object_files[obj]))
            click.echo('    {:10}: {}'.format(obj, uniq_names))

        click.secho('  Dark fields (`{}`):'.format(DARK), fg='blue')
        for exp in conf_dic['exposures']:
            uniq_names = set(map(handy, dark_files[exp])) or None
            click.echo('    {:10}: {}'.format('{}ms'.format(exp), uniq_names))

        click.secho('  Flat fields (`{}`):'.format(FLAT), fg='blue')
        for filt in conf_dic['filters']:
            uniq_names = set(map(handy, flat_files[filt]))
            click.echo('    {:10}: {}'.format(filt, uniq_names))

    # STEP 0: Create directory for auxiliary and stacked images if not existent.
    if verbose:
        click.secho('Creating folders to hold master, auxiliary and '
                    'stacked images.', fg='green')

    if not exists(MASTER) and nomaster:
        click.secho('E: You used the `--nomaster` option but there is no '
                    '`MASTER` folder...', fg='red')
        exit(1)

    for folder in [MASTER, TMP, STK]:
        if not exists(folder):
            mkdir(folder)

    # Determine the master files if the `--nomaster` option is off.
    if not nomaster and not astrometryonly:
        # STEP 1: Write the master dark files (medians of darks)
        # for each available exposure.
        click.secho('Writing master dark images:', fg='green')
        all_exposures = conf_dic['exposures']
        available_exposures = [exp for exp in dark_files if dark_files[exp]]
        for exp in available_exposures:
            if verbose:
                click.echo('    {:14} '.format('{} ms...'.format(exp)), nl=False)
            mdark_data = np.median([fits.getdata(_) for _ in dark_files[exp]],
                                   axis=0)
            mdark_header = fits.getheader(dark_files[exp][0])

            # Write fits file and header.
            nname = '{}/mdark_{}.fits'.format(MASTER, exp)
            fits.writeto(nname, mdark_data, mdark_header, overwrite=True)
            fits.setval(nname, 'FILTER', value='        ')
            fits.setval(nname, 'IMAGETYP', value='Dark    ')
            fits.setval(nname, 'EXPTIME', value=float(exp / 1000.), comment=HC)
            fits.setval(nname, 'EXPOSURE', value=float(exp / 1000.), comment=HC)
            fits.setval(nname, 'OBJECT', value='DARK    ')

            if verbose:
                click.echo('Done ({} images).'.format(len(dark_files[exp])))

        # STEP 1.5: If there are some missing darks and the interpolate option
        # is on, then interpolate the master darks.
        # We use least squares linear interpolation, i.e., we calculate `a` and
        # `b` such that (missing_dark) = a * (exposure_time) + b.
        # Exit if there are no darks at all.
        if not available_exposures:
            click.secho('E: There are no dark files at all! '
                        'Cannot interpolate.', fg='red')
            exit(1)

        if len(available_exposures) == 1:
            # If there's only one available exposure time, consider the darks
            # are dominated by the bias, which is likely. In this case:
            # a = 0, b = only_dark.
            only_exp = available_exposures[0]
            only_mdark = fits.getdata('{}/mdark_{}.fits'.format(MASTER,
                                                                only_exp))
            a = np.zeros_like(only_mdark)
            b = only_mdark
        else:
            # If not, if you want to fit y = a * x + b,
            # then the LS solution is:
            # a = (<xy> - <x><y>) / (<x ** 2> - <x> ** 2)
            # b = <y> - a * <x>
            mxy = np.mean([float(exp)
                           * fits.getdata('{}/mdark_{}.fits'.format(MASTER,
                                                                    exp))
                           for exp in available_exposures], axis=0)
            mx = np.mean([float(exp) for exp in available_exposures])
            my = np.mean([fits.getdata('{}/mdark_{}.fits'.format(MASTER, exp))
                          for exp in available_exposures], axis=0)
            mx2 = np.mean([float(exp) ** 2 for exp in available_exposures])

            # a and b.
            a = (mxy - mx * my) / (mx2 - mx ** 2)
            b = my - mx * a

        # Write all the missing master darks!
        click.secho('Interpolating missing master dark images:', fg='green')
        for exp in list(set(all_exposures) - set(available_exposures)):
            if verbose:
                click.echo('    {:14} '.format('{}ms...'.format(exp)), nl=False)
            new_mdark_data = float(exp) * a + b

            # Write fits file and header.
            nname = '{}/mdark_{}.fits'.format(MASTER, exp)
            fits.writeto(nname, new_mdark_data, overwrite=True)
            fits.setval(nname, 'FILTER', value='        ')
            fits.setval(nname, 'IMAGETYP', value='Interpolated dark')
            fits.setval(nname, 'EXPTIME', value=float(exp / 1000.), comment=HC)
            fits.setval(nname, 'EXPOSURE', value=float(exp / 1000.), comment=HC)
            fits.setval(nname, 'OBJECT', value='DARK    ')

            if verbose:
                click.echo('Done.')

        # STEP 2: Write master transmission files for each filter:
        # mtrans = median(normalized(flat - dark of same exposure)).
        click.secho('Calculating master transmission (flat) images:',
                    fg='green')
        # Handy function to extract exposure from flat file name.
        fexp = lambda fname: fname.split('.fit')[0].split('_')[-2]
        for filt in flat_files:
            if verbose:
                click.echo('    {:12}   '.format('{}...'.format(filt)),
                           nl=False)

            # Calculate normalized flats.
            normalized_flats = list()
            for fitsfile in flat_files[filt]:
                tmp = fits.getdata(fitsfile) \
                    - fits.getdata('{}/mdark_{}.fits'.format(MASTER,
                                                             fexp(fitsfile)))
                normalized_flats.append(tmp / tmp.mean(axis=0))

            mtrans_data = np.median(normalized_flats, axis=0)
            mflat_header = fits.getheader(flat_files[filt][0])

            # Write fits file and header for master transmission.
            nname = '{}/mtrans_{}.fits'.format(MASTER, filt)
            fits.writeto(nname, mtrans_data, mflat_header, overwrite=True)
            fits.setval(nname, 'FILTER', value=filt)
            fits.setval(nname, 'IMAGETYP', value='Light Frame')
            fits.setval(nname, 'EXPTIME', value=-1., comment=HC)
            fits.setval(nname, 'EXPOSURE', value=-1., comment=HC)
            fits.setval(nname, 'OBJECT', value='FLAT    ')

            if verbose:
                click.echo('Done ({} images).'.format(len(flat_files[filt])))

    # STEP 3: Reduce all the object images with corresponding filter mtrans
    # and exposure mdark.
    # noastro will hold all the filennames for object images that do not possess
    # the FOV RADEC coordinates in their header. They can not be astrometrically
    # reduced.
    if not astrometryonly:
        noastro = list()
        click.secho('Writing auxiliary object images:', fg='green')
        for obj in object_files:
            if verbose:
                click.echo('    {:12}   '.format('{}...'.format(obj)), nl=False)
            for fname in object_files[obj]:
                bfname = basename(fname)
                filt, exp = fname_bits(bfname)
                # This will be the final aux file name.
                nname = '{}/{}_{}.fits'.format(TMP, bfname.split('.fit')[0], AUX)
    
                # Corresponding master darks and flats. Reading could fail if the
                # user fiddled with the MASTER folder and used `--nomaster`...
                try:
                    mdark_data = fits.getdata('{}/mdark_{}.fits'.format(MASTER,
                                                                        exp))
                    mtrans_data = fits.getdata('{}/mtrans_{}.fits'.format(MASTER,
                                                                          filt))
                except FileNotFoundError:
                    if nomaster:
                        click.secho(f'E: Master files are missing for '
                                    f'({exp}ms, {filt}), are you sure you want to '
                                    'use the `--nomaster` option?', fg='red')
                        exit(1)
                    else:
                        # There are missing flats and darks and we didn't notice it.
                        # It is our fault, do a real crash.
                        raise
    
                # (Raw - Dark) / Trans.
                aux_data = (fits.getdata(fname) - mdark_data) / mtrans_data
                aux_header = fits.getheader(fname)
    
                # Try to initialize astrometric data in aux file header.
                aux_header_init = init_astro_header(aux_header)
                if aux_header_init == -1:
                    # The initialization failed...
                    click.secho('W: Could not initialize astrometric data in `{}` '
                                '(missing RADEC data).'.format(nname), fg='magenta')
                    noastro.append(nname)
                else:
                    # It worked, use the initialized header to write aux file.
                    aux_header = aux_header_init
    
                # Write fits file and header.
                fits.writeto(nname, aux_data, aux_header, overwrite=True)
                fits.setval(nname, 'FILTER', value=filt)
                fits.setval(nname, 'IMAGETYP', value='Light Frame')
                fits.setval(nname, 'EXPTIME', value=float(exp) / 1000, comment=HC)
                fits.setval(nname, 'EXPOSURE', value=float(exp) / 1000, comment=HC)
                fits.setval(nname, 'OBJECT', value=obj)
    
            if verbose:
                click.echo('Done.')

    # STEP 4: For all objects stack (i.e. realign and median) the aux images.
    # You are left with one image per object per filter per exposure.
    if not nostack and not astrometryonly:
        click.secho('Stacking object images:', fg='green')
        for obj in object_files:
            if verbose:
                click.secho('  {}:'.format(obj), fg='blue')
            # Group all the object files by *tag*, i.e. by filter, exposure.
            name_tag_hash = [(basename(fname),
                             '{}'.format(fname_bits(basename(fname))))
                             for fname in object_files[obj]]
            names_per_tag = defaultdict(list)
            for name, tag in name_tag_hash:
                names_per_tag[tag].append(name)

            # Now you align images which have the same tag.
            for tag in names_per_tag:
                # Rebuild filter and exposure from tag (they are those of,
                # e.g., the first name in the list.)
                f, e = fname_bits(names_per_tag[tag][0])
                # This will be the name of the stacked file
                nname = '{}/{}_{}_{}.fits'.format(STK, obj, f, e)
                if verbose:
                    click.echo('    {:23}'.format('{}:{}ms...'.format(f, e)),
                               nl=False)
                # Calculate aligned and medianed image
                # from all images with same tag.
                aux_files = glob('{}/{}_{}_{}_*_{}.fits'.format(TMP, obj, f,
                                                                e, AUX))
                stacked_data = align_and_median(aux_files)
                stacked_header \
                    = fits.getheader('{}/{}'.format(OBJ,
                                                    names_per_tag[tag][0]))
                # Try to initialize astrometric data in stacked file header.
                stacked_header_init = init_astro_header(stacked_header)
                if stacked_header_init == -1:
                    # The initialization failed...
                    click.secho('W: Could not initialize astrometric data in '
                                '`{}` (missing RADEC data).'.format(nname),
                                fg='magenta')
                else:
                    # It worked, use the initialized header for stacked file.
                    stacked_header = stacked_header_init

                # Write fits file and header.
                fits.writeto(nname, stacked_data, stacked_header,
                             overwrite=True)
                fits.setval(nname, 'FILTER', value=f)
                fits.setval(nname, 'IMAGETYP', value='Light Frame')
                fits.setval(nname, 'EXPTIME', value=float(e) / 1000.,
                            comment=HC)
                fits.setval(nname, 'EXPOSURE', value=float(e) / 1000.,
                            comment=HC)
                fits.setval(nname, 'OBJECT', value=obj)
                if verbose:
                    click.echo('       Done ({} images).'
                               ''.format(len(aux_files)))

    # STEP 5: If options stkpng or tmppng are on, write
    # PNG versions of all the auxiliary, master and stacked images.
    if stkpng and not astrometryonly:
        click.secho('Writing PNG versions of stacked images... ',
                    fg='green', nl=False)
        for ffile in glob('{}/*.fits'.format(STK)):
            write_png(ffile, plt)
        click.secho('Done.', fg='green')

    if tmppng and not astrometryonly:
        click.secho('Writing PNG versions of master and auxiliary images... ',
                    fg='green', nl=False)
        for ffile in glob('{}/*.fits'.format(TMP)):
            write_png(ffile, plt)
        for ffile in glob('{}/*.fits'.format(MASTER)):
            write_png(ffile, plt)
        click.secho('Done.', fg='green')

    # STEP 6: If options sex, psfex or sexagain are on,
    # run the astromatic suite.
    # Sexagain implies psfex, psfex implies sex and scamp implies sex.
    #sex = not astrometrynet_online
    psfex = not astrometrynet_online and not astrometrynet_local
    scamp = not astrometrynet_online and not astrometrynet_local
    psfex = psfex or sexagain
    sex = sex or psfex
    sex = sex or scamp
    if sex or psfex or sexagain or scamp:
        # Announce the suite of astromatic commands we will launch.
        click.secho('Starting astrometry reduction.\n'
                    'We will be running the following Astromatic commands: '
                    '{}.'.format(', '.join(filter(eval, ASTROMATIC_LIST))),
                    fg='green')
        # Setup for the astrometry: initialize empty result folders.
        for folder in [SEX_RES, PSFEX_RES, SCAMP_RES, RED]:
            if exists(folder):
                rmtree(folder, ignore_errors=True)
            mkdir(folder)

        # Setup for the astrometry: find configuration files in the file system.
        t120_sex = resource_filename(AR, '{}/{}'.format(DATA, T120_SEX))
        t120_param = resource_filename(AR, '{}/{}'.format(DATA, T120_PARAM))
        t120_psfex = resource_filename(AR, '{}/{}'.format(DATA, T120_PSFEX))
        t120_parampsfex = resource_filename(AR, '{}/{}'.format(DATA,
                                                               T120_PARAMPSFEX))
        default_conv = resource_filename(AR, '{}/{}'.format(DATA, DEFAULT_CONV))
        t120_scamp = resource_filename(AR, '{}/{}'.format(DATA, T120_SCAMP))
        t120_ahead = resource_filename(AR, '{}/{}'.format(DATA, T120_AHEAD))

    # Run sextractor.
    if sex:
        for ffile in glob('{}/*.fits'.format(TMP))+\
                     glob('{}/*.fits'.format(STK)):
            if ffile in noastro:
                click.secho('W: Missing astrometry data in file `{}`, '
                            'skipping sex run. '.format(ffile), fg='magenta')
                continue
            stem = basename(ffile.split('.fit')[0])
            sex_cmd = SEX_CMD.format(ffile, t120_sex, t120_param, default_conv,
                                     SEX_RES, stem + '.ldac',
                                     SEX_RES, stem + '-bckg.fits',
                                     SEX_RES, stem + '-obj.fits',
                                     SEX_RES, stem + '.xml')
            if verbose:
                click.secho('  Submitting SExtractor command: '
                            '{}'.format(sex_cmd), nl=True, fg='blue')
            system(sex_cmd)

    # Run PSFEx with sextractor-determined sources.
    if psfex:
        for ffile in glob('{}/*.fits'.format(TMP)):
            if ffile in noastro:
                click.secho('W: Missing astrometry data in file `{}`,'
                            'skipping psfex run. '.format(ffile), fg='magenta')
                continue
            stem = basename(ffile.split('.fit')[0])
            psfex_cmd = PSFEX_CMD.format(t120_psfex, stem + '.xml')
            if verbose:
                click.secho('  Submitting PSFex command: {}'.format(psfex_cmd),
                            nl=True, fg='blue')
            system(psfex_cmd)

    # Run sextractor with PSFEx-determined PSF.
    if sexagain:
        for ffile in glob('{}/*.fits'.format(TMP)):
            if ffile in noastro:
                click.secho('W: Missing astrometry data in file `{}`, '
                            'skipping second sex run.'.format(ffile),
                            fg='magenta')
                continue
            stem = basename(ffile.split('.fit')[0])
            sexagain_cmd = SEX_CMD.format(ffile, t120_sex, t120_parampsfex,
                                          default_conv,
                                          SEX_RES, stem + '.ldac',
                                          SEX_RES, stem + '-bckg.fits',
                                          SEX_RES, stem + '-obj.fits',
                                          SEX_RES, stem + '.xml')\
                + SEXAGAIN_OPT_CMD.format(stem + '.psf')
            if verbose:
                click.secho('  Submitting second SExtractor command: '
                            '{}'.format(sexagain_cmd), nl=True, fg='blue')
            system(sexagain_cmd)
    
    # Run SCAMP.
    if scamp:
        listldac = glob('{}/*.ldac'.format(SEX_RES))
        scamp_cmd = SCAMP_CMD.format(' '.join(listldac), t120_scamp, t120_ahead)
        if verbose:
            click.secho('  Submitting SCAMP command: {}'.format(scamp_cmd),
                        nl=True, fg='blue')
        system(scamp_cmd)

        # Read scamp result.
        scampxml = 'scamp.xml'
        votable = parse(scampxml)
        table = votable.get_first_table()
        catcont = Table([(table.array['Catalog_Name']).data,
                        (table.array['XY_Contrast']).data],
                        names=['name', 'contrast'])

        min_contrast = 10.0
        # Update astrometry info in fits headers with Scamp results.
        for fhed in glob('{}/*.head'.format(SEX_RES)):
            # Get/set original/reduced image file name.
            key = splitext(basename(fhed))[0].replace('_aux', '')
            fori = '{}/{}'.format(UOBJ, u2ar[key])
            fred = '{}/{}'.format(RED, basename(fori))
            ffts = '{}/{}'.format(TMP, basename(fhed.replace('.head', '.fits')))
            # Check if SCAMP contrast is enough.
            mask = catcont['name'] == basename(fhed).replace('.head', '.ldac')
            contrast = catcont[mask]['contrast'][0]
            click.secho('`{}` = contrast: {}'.format(fori, contrast))
            if (contrast < min_contrast):
                click.secho('W: Contrast too low ({}) for `{}`'.format(contrast,
                                                                       fori),
                            fg='magenta')
                remove(fhed)
                remove(fhed.replace('.head', '.ldac'))
                continue

            # Update header for reduced file.
            red_data = fits.getdata(ffts)
            red_header = fits.Header.fromtextfile(fhed)
            fts_header = fits.getheader(ffts)
            # Write first version of fits file for reduced image.
            fits.writeto(fred, red_data, fts_header, overwrite=True)
            # Now update header.
            for hdr_key in red_header:
                if hdr_key == 'HISTORY' or hdr_key == 'COMMENT' or 'FLXSCALE':
                    continue
                fits.setval(fred, hdr_key, value=red_header[hdr_key])

            if verbose:
                click.secho('Reduced data saved in `{}`.'.format(fred))

    # if astrometry.net
    if astrometrynet_online or astrometrynet_local:
        if verbose:
            click.secho('  Launching astrometry.net ', nl=True)#, fg='blue')
        # Setup for the astrometry: initialize empty result folders.
        for folder in [SEX_RES, RED]:
            if not exists(folder):
                mkdir(folder)
        
        # Setup for the astrometry: find configuration files in the file system.
        t120_sex = resource_filename(AR, '{}/{}'.format(DATA, T120_SEX))
        t120_param = resource_filename(AR, '{}/{}'.format(DATA, T120_PARAM))
        t120_psfex = resource_filename(AR, '{}/{}'.format(DATA, T120_PSFEX))
        default_conv = resource_filename(AR, '{}/{}'.format(DATA, DEFAULT_CONV))
        
        # make list of files to get astrometry
        listfits = glob('{}/*.fit*'.format(TMP))+glob('{}/*.fit*'.format(STK))
        listfits.sort()
        
        # Run sextractor.
        if astrometrynet_online:
            for ffile in listfits:
                # construct dat file name
                stem = basename(ffile.split('.fit')[0])
                datfile = '{}/{}'.format(SEX_RES,stem + '.dat')
                if not forceimg:
                    if exists(datfile):
                        click.secho('File '+datfile+' already exist: skip Sextrator',fg='blue')
                    else:
                        sex_cmd = SEX_NET.format(ffile, t120_sex, t120_param,
                                                 default_conv,
                                                 SEX_RES, stem + '.dat',
                                                 SEX_RES, stem + '.xml')
                        if verbose:
                            click.secho('  Submitting SExtractor command: '
                                        '{}'.format(sex_cmd), nl=True, fg='blue')
                        system(sex_cmd)
        
        # following line removed since conflicts sometimes happen: fdat does NOT correspond to fimg
        #for (fdat,fimg) in zip(listdat,listfits):
        for fimg in listfits:
            # skip if reduced file already exist
            fred = '{}/{}'.format(RED, basename(fimg))
            if exists(fred):
                click.secho('Reduced image: {} already exists: skipping astrometry.'.format(fred), fg='blue')
                continue
            
            # read image
            hdu     = fits.open(fimg)
            header  = hdu[0].header
            data    = hdu[0].data
            hdu.close()    
            
            # run astrometry.net online version
            if astrometrynet_online:
                # (re)-construct dat file name
                stem = basename(fimg.split('.fit')[0])
                fdat = '{}/{}'.format(SEX_RES,stem + '.dat')
                if not forceimg:
                    # read Sextractor output
                    if verbose:
                        click.secho('==============', fg='green')
                        click.secho('Processing image: {}'.format(fimg), fg='green')
                        click.secho('Reading dat file: {}'.format(fdat), fg='green')
                    sources = Table.read(fdat,format='ascii.sextractor')
                    sources.sort('FLUX_APER')
                    sources.reverse()
                    nsrc = len(sources)
                    # next if not enough sources
                    if verbose:
                        click.secho('{} sources found in dat file: {}'.format(nsrc,fdat), fg='green')
                    if (nsrc<STRNB_MIN):
                        click.secho('{} is NOT ENOUGH sources found in dat file: {}'.format(nsrc,fdat), fg='red')
                        click.secho('{} is is ignored for further astrometry consideration'.format(fimg), fg='red')
                        continue

                (image_width,image_height) = data.shape
                try:
                    skycoo_i = SkyCoord(ra=header['OBJCTRA'],dec=header['OBJCTDEC'],
                                        unit=(u.hourangle, u.deg), frame="icrs")
                    click.secho('T120 RA/DEC: '+skycoo_i.to_string(style='hmsdms'),
                                fg='green')
                except:
                    click.secho('W: No astrometry info in header', fg='magenta')
            
                # create astrometry.net object.
                ast = AstrometryNet()
                ast.api_key = 'ibluryspyzhcbyny'
                wcs_header = None
                keeptrying = True
                submission_id = None
                
                while keeptrying:
                    try:
                        if not submission_id:
                            if forceimg:
                                click.secho('Sending {} to astrometry.net'.format(fimg), fg='magenta')
                                wcs_header = ast.solve_from_image(fimg,
                                                                  force_image_upload=True,
                                                                  solve_timeout=120)
                            else:
                                click.secho('Sending sources from {} to astrometry.net'.format(fdat), fg='magenta')
                                wcs_header, submission_id = ast.solve_from_source_list(sources['X_IMAGE'],
                                                                sources['Y_IMAGE'],
                                                                image_width,
                                                                image_height,
                                                                solve_timeout=120,
                                                                verbose=True,
                                                                return_submission_id=True,
                                                                scale_est=0.77,
                                                                scale_units='arcsecperpix',
                                                                scale_type='ev',
                                                                scale_err=5.0,
                                                                parity=2)
                        else:
                            click.secho(' *** monitoring submission_id: {}'.format(submission_id),nl=True, fg='magenta')
                            wcs_header = ast.monitor_submission(submission_id,
                                                                solve_timeout=360, verbose=True)
                    # possible exception: TimeoutError, ConnectionError, RuntimeError
                    except Exception as e:
                        try:
                            submission_id = e.args[1]
                            click.secho(' *** TimeoutError submission_id: {}'.format(submission_id),nl=True, fg='magenta')
                        except:
                            click.secho(' *** Exception: {}'.format(type(e).__name__),nl=True, fg='magenta')
                            #click.secho(' Submission_id = : {}'.format(str(submission_id)),nl=True, fg='magenta')
                    else:
                        keeptrying = False
                        click.secho(' *** Astrometry reduction successful!',fg='green')           
            
            # run astrometry.net localy
            if astrometrynet_local:
                astronet_cfg = resource_filename(AR, '{}/{}'.format(DATA, ASTRONET_CFG))
                #astronet_cfg = '{}/{}/{}/{}'.format(package_dir, AR, DATA, ASTRONET_CFG)
                astronet_cmd = ASTRONET_CMD.format(astronet_cfg, ASTRONET_DIR, fimg)
                #astronet_cmd = ASTRONET_CMD.format(ASTRONET_DIR, fimg)
                hdr_file = '{}/{}.{}'.format(SEX_RES, Path(fimg).stem,'wcs')
                
                # submit command
                if verbose:
                    click.secho('  Submitting Astrometry.net command: '
                                '{}'.format(astronet_cmd), nl=True, fg='blue')
                try:
                    system(astronet_cmd)
                except:
                    click.secho('*** Impossible to submit command '
                                '{}'.format(astronet_cmd),nl=True,fg='magenta')
                
                # check output wcs header
                if not os.path.exists(hdr_file):
                    click.secho('*** Astrometry failed for {}'.format(fimg),nl=True, fg='red')
                    click.secho('{} will NOT appear in the reduction directory'.format(fimg), fg='magenta')
                    continue
                # read header file
                wcs_header = fits.Header.fromfile(hdr_file)
            
            # save header info                
            for hdrkey in wcs_header[5:]:
                # stop at date keyword to avoid filling the header with loads of comments
                if (hdrkey=='DATE'):
                    header.add_history('WCS info created by Astrometry.net.')
                    break
                try:
                    header[hdrkey] = wcs_header[hdrkey]
                except:
                    if (hdrkey=='HISTORY'):
                        continue
                    else:
                        click.secho('Impossible to save header key: {}'.format(str(hdrkey)),fg='magenta')  
                

            try:
                skycoo_f = SkyCoord(ra=wcs_header['CRVAL1']*u.deg,
                                    dec=wcs_header['CRVAL2']*u.deg, frame="icrs")
                click.secho('True RA/DEC: '+skycoo_f.to_string(style='hmsdms'),
                            fg='green')
            except:
                click.secho('*** Astrometry failed for {}'.format(fimg),nl=True, fg='red')
                click.secho('{} will NOT appear in the reduction directory'.format(fimg), fg='magenta')
            
            # save in output file
            fred = '{}/{}'.format(RED, basename(fimg))
            fits.writeto(fred, data, header,output_verify='fix', overwrite=True)
            click.secho('file saved in {}'.format(fred),fg='green')

    # Report execution time.
    t1 = time()
    click.secho('\nastro_reduce done. ({})'.format(timedelta(seconds=int(t1 - t0))),
                fg='green')
    # ALL DONE.
