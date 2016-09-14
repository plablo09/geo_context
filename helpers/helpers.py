# -*- coding: utf-8 -*-
import numpy as np
from collections import Counter

def make_binary(original_data, pos_classes):
    """Returns binary classes."""
    # data is an array of class numbers or names.
    # If an class member is in pos_classes, change it to 1 else 0
    return np.array([(1 if val in pos_classes else 0)
                     for val in original_data ])

def flip_labels(original_data):
    """Flips class labels."""
    return np.array([1 if val == 0 else val for val in original_data])

def class_info(classes):
    """Prints classes info"""
    counts = Counter(classes)
    total = sum(counts.values())
    for cls in counts.keys():
        print("%6s: % 7d  =  % 5.1f%%" % (cls, counts[cls], counts[cls]/total*100))