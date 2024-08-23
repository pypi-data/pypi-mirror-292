# Copyright (C) 2024 Jaehak Lee

import json
import numpy as np
import pandas as pd

class LabeledTensor(object):
    def __init__(self, data, labels=None, label_names=None):
        if type(data) == list:
            data = np.array(data)
        elif type(data).__name__ in ["int","float","complex"]:
            data = np.array([data])
        else:
            data = np.array(data)      
        self.data = data
        if labels:
            self.labels = labels
        else:
            self.labels = [[i for i in range(self.data.shape[j])] for j in range(len(self.data.shape))]
        if label_names:
            self.label_names = label_names
        else:
            self.label_names = ["axis"+str(i) for i in range(len(self.data.shape))]            
    
    def to_chart_data(self):
        if len(self.data.shape) == 1:
            data_dict = {"x":self.labels[0], "y":self.data}            
            return data_dict, *self.label_names
        else:
            print(self.data, self.data.shape)
            print("only 1d data is supported for now.")
            return None

    def set_chart_data(self, data_dict):
        if len(self.data.shape) == 1:
            if len(self.labels) == 0:
                self.data = np.array(data_dict["y"])
            else:
                self.data = np.array(data_dict["y"])
                self.labels[0] = data_dict["x"]
        else:
            print("only 1d data is supported for now.")
            return None

    def to_np_dict(self):
        return {"data": self.data, "labels": self.labels, "label_names": self.label_names}
    
    def from_np_dict(data_dict):
        data = data_dict["data"]
        if "labels" in data_dict.keys():
            labels = data_dict["labels"]
        else:
            labels = []
        if "label_names" in data_dict.keys():
            label_names = data_dict["label_names"]
        else:
            label_names = ["axis"+str(i) for i in range(len(data.shape))]
        return LabeledTensor(data, labels, label_names)

    def to_json_dict(self):
        data_list = self.data.tolist()
        return {"data": data_list, "labels": self.labels, "label_names": self.label_names}
    
    def from_json_dict(json_dict):
        data = np.array(json_dict["data"])
        if "labels" in json_dict.keys():
            labels = json_dict["labels"]
        else:
            labels = []
        if "label_names" in json_dict.keys():
            label_names = json_dict["label_names"]
        else:
            label_names = ["axis"+str(i) for i in range(len(data.shape))]
        return LabeledTensor(data, labels, label_names)
        
    def shape(self):
        return self.data.shape

    def get_labels(self):
        labels = []
        for i in range(len(self.shape())):
            if i < len(self.labels):
                if self.shape()[i] == len(self.labels[i]):
                    labels.append(self.labels[i])
                else:
                    print("Warning: shape of labels does not match shape of data")
                    labels.append(list(range(self.shape()[i])))
            else:
                labels.append(list(range(self.shape()[i])))
        return labels
    
    def get_label_names(self):
        label_names = []
        for i in range(len(self.shape())):
            if i < len(self.label_names):
                label_names.append(self.label_names[i])
            else:
                label_names.append("axis"+str(i))
        return label_names

            
        
            

