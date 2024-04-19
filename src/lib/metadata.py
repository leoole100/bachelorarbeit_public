import os
import re
import pandas as pd


# #############################################################################
# Extract metadata from filename for spectra
# #############################################################################
def get_name(path):
    return path.split("data/")[-1]

def get_date(path):
    date_string = get_name(path).split("/")[0][:10]
    return pd.to_datetime(date_string)

def fname_parts(path):
    fname = os.path.basename(path)
    fname = ".".join(fname.split(".")[:-1]) # remove extension
    return fname.split("_")

def extract_number(parts):
    """
    important: has to be extracted first
    integer + "d"
    """
    if parts[0][0] == "d":
        return (parts[1:], int(parts[0][1:]))
    else: 
        return (parts, None)

def extract_temperature(parts):
    """
    float + "K"
    """
    for p in parts:
        if p[-1] == "K":
            parts.remove(p)
            # return (parts, float(p[:-1]))
            return (parts, float(re.sub("[^0-9.\-]","",p)))
    return (parts, None)

def extract_angle(parts):
    """
    float + "K"
    """
    for p in parts:
        if p[-3:-1] == "deg":
            parts.remove(p)
            return (parts, float(p[:-4]))
    return (parts, None)

def extract_capture(parts):
    """
    string + "s"
    """
    for p in parts:
        if p[-1] == "s":
            parts.remove(p)
            return (parts, p)
    return (parts, None)

__material_dict__ = {
    "CrPS4": "CrPS4",
    "CrPS3": "CrPS4", # typo in filename
    "CrPS": "CrPS4",
    "FePS3": "FePS3",
    "FePS": "FePS3",
    "MnPS3": "MnPS3",
    "MnPS": "MnPS3",
    "NnPS3": "MnPS3", # typo in filename
    "NiPS3": "NiPS3",
    "NiPS": "NiPS3",
    "copper": "Cu",
    "mirror": "mirror",
    "glass": "glass",
    "Si": "Si",
    "SiO2": "SiO2",
    "SiO": "SiO2",
}

def extract_material(parts):
    """
    extracts the material from material_dict
    """
    for m in __material_dict__.keys():
        if m in parts:
            # remove material from parts
            parts.remove(m)
            return (parts, __material_dict__[m]) 
    return (parts, None)
        
__methods_dict__ = {
    "refl": "reflectance",
    "ref": "reflectance",
    "re": "reflectance",
    "REF": "reflectance",
    "lm": "luminescence",
    "lum": "luminescence",
}

def extract_method(parts):
    """
    extracts the method from methods_dict
    """
    for m in __methods_dict__.keys():
        if m in parts:
            parts.remove(m)
            return (parts, __methods_dict__[m])
    return (parts, None)

def extract_metadata(path):
    """
    Extract metadata from filename.
    """
    parts = fname_parts(path)
    metadata = {}
    parts, metadata["experiment"] = extract_number(parts)
    parts, metadata["material"] = extract_material(parts)
    parts, metadata["method"] = extract_method(parts)
    parts, metadata["capture"] = extract_capture(parts)
    parts, metadata["temperature"] = extract_temperature(parts)
    parts, metadata["angle"] = extract_angle(parts)
    metadata["name"] = get_name(path)
    metadata["date"] = get_date(path)
    if parts:
        metadata["remaining"] = parts
    else: 
        metadata["remaining"] = None
    metadata["path"] = path

    return metadata
