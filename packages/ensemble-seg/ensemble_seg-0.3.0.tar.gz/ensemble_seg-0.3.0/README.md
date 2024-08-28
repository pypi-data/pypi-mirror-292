# ensemble_seg

Agnostic ensemble algorithm for instance segmentation tasks

| Augmentation 1 | Augmentation 2 | Augmentation 3 |
| --- | --- | --- |
| ![Original 0](/graphics/original_0.jpg) | ![Original 1](/graphics/original_1.jpg) | ![Original 2](/graphics/original_2.jpg)

| Blended Ensemble |
| --- |
| <img src="/graphics/blended.jpg" width="500" /> |



# Problem Statement

Instance segmentation models are typically trained on a variety of data augmentation techniques to improve generalization. However, the real data
may not always contain representations of augmented data that the training set contained. Further, ensemble methods and algorithms to merge predictions from segmentation models are quite verbose.

# Solution

This `ensemble_seg` codebase provides a simple, model agnostic interface to blend multiple predictions from an instance segmentation model into single contained predictions. Designed to be simple to use and optimized for speed with Numpy, OpenCV, and Numba powered functions.

# How to Use

See the `example` directory with a full example notebook reading contours from a coco dataset and blending them together.

## Install

```bash
pip install ensemble-seg
```

## Detectron2 Predictions

Prepare augmentations and format predictions

```python

# load the image and augment it however many times you want
frame = cv2.imread('/path/to/frame.jpg')

augmented = []
for _ in range(3):
    augmented.append(transformer(image=frame)['image'])

# run the predictions on each augmented image
results = []
for image in [frame] + augmented:
    instances = predictor(image)['instances'].to('cpu')

    # format the predictions
    for i, pred_mask in enumerate(instances.pred_masks)
        mask = pred_mask.numpy().astype(np.uint8)
        bbox = instances.pred_boxes[i].tensor.numpy().astype(np.int32)[0]

        # only keep mask within bbox. set the mask outside bbox to 0
        mask[:bbox[1], :] = 0
        mask[bbox[3]:, :] = 0
        mask[:, :bbox[0]] = 0
        mask[:, bbox[2]:] = 0

        results.append({ 'mask': mask, 'bbox': bbox })
```

Blend the predictions together!

```python
from ensemble_seg import merge_masks

for group, mask in merge_masks(results):
    # group contains the indices of the masks that were merged
    # mask is the blended mask
```

# For Development

## Build
```
python3 setup.py sdist bdist_wheel
```

## Publish
```
python3 -m twine upload --skip-existing dist/*
```