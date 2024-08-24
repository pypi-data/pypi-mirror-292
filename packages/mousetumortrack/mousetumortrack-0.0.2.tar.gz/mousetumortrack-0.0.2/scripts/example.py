import sys
import tifffile
from time import perf_counter

from mousetumortrack import run_tracking

if __name__=='__main__':
    _, labels_timeseries_file, images_series_file = sys.argv
    labels_timeseries = tifffile.imread(labels_timeseries_file)
    images_timeseries = tifffile.imread(images_series_file)
    n_frames = len(labels_timeseries)

    # With Trackpy
    t0 = perf_counter()
    *_, labels_timeseries_trackpy = run_tracking(labels_timeseries, method="trackpy")
    print(perf_counter() - t0)

    # With Laptrack
    t0 = perf_counter()
    *_, labels_timeseries_laptrack = run_tracking(labels_timeseries, method="laptrack")
    print(perf_counter() - t0)

    # With Laptrack and mouselungseg registration
    t0 = perf_counter()
    *_, labels_timeseries_laptrack_reg = run_tracking(
        labels_timeseries,
        image_timeseries=images_timeseries,
        with_lungs_registration=True, 
        method="laptrack",
    )
    print(perf_counter() - t0)

    # import napari
    # viewer = napari.Viewer(ndisplay=3)
    # viewer.add_labels(labels_timeseries, name="Labels (Untracked)")
    # viewer.add_labels(labels_timeseries_trackpy, name="Labels (Trackpy)")
    # viewer.add_labels(labels_timeseries_laptrack, name="Labels (Laptrack)")
    # viewer.add_labels(labels_timeseries_laptrack_reg, name="Labels (Laptrack+reg)")
    # napari.run()