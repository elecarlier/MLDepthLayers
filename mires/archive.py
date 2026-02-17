def Set_tiff_voxel_size(file_path, ResX, ResY):
    """
    Implemented based on information found in https://pypi.org/project/tifffile
    """

    def _xy_voxel_size(tags, key):
        assert key in ['XResolution', 'YResolution']
        if key in tags:
            num_pixels, units = tags[key].value
            return units / num_pixels
        # return default
        return 1.

    with tifffile.TiffFile(file_path, mode="r+b") as tiff:
        
        # image = imread(file_path)
        image_metadata = tiff.imagej_metadata
        
        if image_metadata is not None:
            z = image_metadata.get('spacing', 1.)
        else:
            # default voxel size
            z = 1.

        tags = tiff.pages[0].tags

        tagYR = tags['YResolution']
        tagXR = tags['XResolution']

        print("Trouvé : ", tagXR.value[0], tagYR.value[0], tagYR.value[1])

        resUnit = int(tagYR.value[1])
        YR0 = ResY*resUnit
        XR0 = ResX*resUnit
        
        print("Nouvelles valeurs :", XR0, YR0, resUnit)

        tagYR.overwrite((YR0,resUnit))
        tagXR.overwrite((XR0,resUnit))
        

        # parse X, Y resolution

        y = _xy_voxel_size(tags, 'YResolution')
        x = _xy_voxel_size(tags, 'XResolution')
        
        #print (x)
        #print (y)
        
        # return voxel size
        return [z, y, x]
