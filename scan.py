#!/usr/bin/python3
# photoscan bits
# 8/28/18
# updated 8/28/18

import os
import PhotoScan as scan

photo_dir = '~/Desktop/phtscn'
doc = scan.app.document
chunk = doc.addChunk()

# using os.listdir since photoscan's python (3.3) doesn't have os.scandir
photos = ['{}'.format(os.path.join(photo_dir, photo)) for photo in os.listdir(photo_dir)]
chunk.addPhotos(photos)

# check metadata for a camera
chunk.cameras[0].photo.meta

# process photos
chunk.matchPhotos(accuracy=scan.HighAccuracy)
chunk.alignPhotos()
chunk.buildDenseCloud()
chunk.buildModel()
