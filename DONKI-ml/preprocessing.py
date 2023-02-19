#!/usr/bin/env python3
import os
import pandas as pd

# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html#sklearn.preprocessing.OneHotEncoder
from sklearn.preprocessing import OneHotEncoder

data = os.getenv("DATA_DIR", "../data/2023-02-18-2023-01-19DONKI.json")

df = pd.read_json(data, orient="records")
df = df.drop(columns=['messageID', 'messageURL', 'messageIssueTime', 'messageBody'])

# encode messageType field
messageTypes = df["messageType"].unique().tolist()
enc = OneHotEncoder(categories=[messageTypes])
enc.fit(df.values)

# see each type and its encoding
for t in messageTypes:
    print(t, enc.transform([[t]]).toarray())

"""
CME [[1. 0. 0. 0. 0.]]
FLR [[0. 1. 0. 0. 0.]]
RBE [[0. 0. 1. 0. 0.]]
Report [[0. 0. 0. 1. 0.]]
IPS [[0. 0. 0. 0. 1.]]
"""



