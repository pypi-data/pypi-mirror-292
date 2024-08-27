from PIL import Image, ExifTags


def print_exif_data(img_path):
    img = Image.open(img_path)
    img_exif = img.getexif()
    print(type(img_exif))

    if img_exif is None:
        print('Sorry, image has no exif data.')
    else:
        for key, val in img_exif.items():
            if key in ExifTags.TAGS:
                print(f'{ExifTags.TAGS[key]}:{val}')
            else:
                print(f'{key}:{val}')


if __name__ == '__main__':
    print_exif_data('yoga.jpg')


"""
<class 'PIL.Image.Exif'>
GPSInfo:21360
ResolutionUnit:2
ExifOffset:348
Make:NIKON CORPORATION
Model:NIKON D850
Software:Ver.1.20 
Orientation:8
DateTime:2022:06:26 12:41:48
YCbCrPositioning:2
YResolution:300.0
Copyright:                                                      
XResolution:300.0
Artist:                                    
"""