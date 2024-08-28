#!/usr/bin/python3

import pytest, h5py, numpy, xarray

from nx5d.xrd import kmc3

from nx5d.xrd import signal

from pprint import pprint

# It's difficult (impossible?) to actually test whether LazyQMap
# truly delivers physically correct results. What we're focusing
# on here primarily is testing whether the interface behaves as
# expected, and data dimensionality is as we want it to be.

def data_dict(num_images=64, img_size=None, **extra_data):
    # Creates a dictionary of test data with `num_images` images.
    # If `img_size` is not defined, the size of the default kmc3
    # detector (pilatus) is used.
    #
    # `extra_data` is an additional dictionary of data, expected
    # to have the same dimensionality as the `num_images`. It
    # will be added to the dictionary.
    #
    # The dictionary structure is... biased: a main key 'angles'
    # will hold the specific angles (phi, chi, omega, twotheta).
    # The rest of the data (images, extra_data) are flat alongside
    # the angles.
    
    num_imgs = 64
    
    if img_size is None:
        img_size = kmc3.ExperimentTemplate['imageSize']
        
    return {
        'images': numpy.ndarray((num_images, *img_size)),
        'angles': {
            'phi': numpy.array([.0]*num_images),
            'chi': numpy.array([.0]*num_images),
            'theta': numpy.array(range(num_images))*0.01 + 12.0,            
            'twotheta': numpy.array(range(num_images))*0.01 + 24.0
        },
        **extra_data
    }
    
@pytest.fixture
def h5data():
    # Generating an artificial HDF5 dataset of ~50 images
    #with h5py.File() as h5:
    #    return h5
    pass

@pytest.fixture
def xrdata(data=None, index=None, **extra_data):
    # Returning an xarray.Dataset with ~50 images and corresponding angles.
    # Structurally this is different from the data_dict: _all_ data is flat,
    # including the angles.
    #
    # Returns a (dataset, exp_setup) tuple.

    if data is None:
        num_images = 64
        img_size = kmc3.ExperimentTemplate['imageSize']
        data = data_dict(num_images)

    coords = {
        'index': index if index is not None \
            else numpy.array(range(data['images'].shape[0])),
        'x': numpy.array(range(data['images'].shape[1])),
        'y': numpy.array(range(data['images'].shape[2])),
    }
            # 
    dvars = { k: ('index', v) for k,v in data['angles'].items() }
    dvars.update({ k: ('index', v) for k,v in extra_data.items() })
    dvars['images'] = ('index', 'x', 'y'), data['images']

    # Create an experimental setup suitable for this module's test data
    # (based on the KMC3 experimental setup).
    # Differently from a HDF5-based data dictionary, _all_ the data
    # is inside the `ds` Dataset here.
    ds = xarray.Dataset(coords=coords, data_vars=dvars)
    exp_setup = kmc3.ExperimentTemplate.copy()
    exp_setup.update({

        # All the angles are in the Dataset already. Here we just
        # need to name which data-vars  are to be attributed to the angles.
        'detectorTARAngles': {
            'twotheta': "@twotheta"
        },
        'goniometerAngles': {
            'chi': "@chi",
            'phi': "@phi",
            'theta': "@theta"
        },

        # Need some fake data (which won't be readable from Dataset)
        'beamEnergy': 9600.0,
        'imageDistance': 720.0,
    })

    return ds, exp_setup


def test_data(xrdata):
    print (xrdata[0])
    pprint(xrdata[1])

    
def test_qmapper(xrdata):

    # setup in xrdata contains 'goniometerAngles' and 'detectorTARAngles'.
    clean_setup_no_angles = {
        k:xrdata[1][k] for k in filter(lambda x: not x.endswith('Angles'), xrdata[1])
    }

    print("Clean setup, no angle names:")
    pprint(clean_setup_no_angles)

    # re-introduce angle names in 'Axes' parameters -> make them dict()s
    clean_setup_with_angles = clean_setup_no_angles.copy()
    clean_setup_with_angles['goniometerAxes'] = {
        k:v for k,v in zip(xrdata[1]['goniometerAngles'].keys(),
                           clean_setup_no_angles['goniometerAxes'])
    }
    clean_setup_with_angles['detectorTARAxes'] = {
        k:v for k,v in zip(xrdata[1]['detectorTARAngles'].keys(),
                           clean_setup_no_angles['detectorTARAxes'])
    }

    print("Clean setup, with angle names:")
    pprint(clean_setup_with_angles)


    ## selecting full image
    q = signal.QMapper(**clean_setup_no_angles)
    with pytest.raises(signal.InsufficientAngles):
        # This is supposed to fail (default 'setup' does not include angle names)
        q.qmap(xrdata[0])
    q.qmap(xrdata[0], angles=('chi', 'phi', 'theta', 'twotheta'))

    ## selecting with ROI
    q = signal.QMapper(**clean_setup_with_angles, roi=(0, 100, 0, 200))
    q.qmap(xrdata[0].isel(x=slice(0,100), y=slice(0,200)))

    ## plain selection, no ROI, with angles
    q = signal.QMapper(**clean_setup_with_angles)
    with pytest.raises(RuntimeError):
        # must fail because default selection is 3 axes
        q.qmap(xrdata[0], qsize=(100, 100))
    q.qmap(xrdata[0], dims=('qx', 'qy'))
    q.qmap(xrdata[0], qsize=dict(qx=100, qy=300))
    q.qmap(xrdata[0])

    data = q.qmap(xrdata[0])

    print(data)
