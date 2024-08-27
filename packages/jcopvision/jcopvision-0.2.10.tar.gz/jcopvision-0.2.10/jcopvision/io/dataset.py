from pathlib import Path
import xml.etree.ElementTree as ET


def read_pascal_xml(fname, classes, exclude_classes=[], exclude_truncated=True, exclude_difficult=True):
    fname = Path(fname)
    assert fname.suffix == ".xml"
    
    data = ET.parse(fname).getroot()
    size = data.find('size')
    c = int(size.find('depth').text)
    h = int(size.find('height').text)     
    w = int(size.find('width').text)
    parsed = {
        "filename": data.find("filename").text,
        "size": (h, w, c),
        "segmented": bool(data.find("segmented").text),
        "object": []
    }

    yolo_bboxs = []
    for obj in data.iter('object'):
        name = obj.find('name').text
        difficult = int(obj.find('difficult').text)
        truncated = int(obj.find('truncated').text)  

        if (name in exclude_classes) or (name not in classes):
            continue

        if exclude_difficult and difficult:
            continue

        if exclude_truncated and truncated:
            continue

        label_id = classes.index(name)
        bndbox = obj.find('bndbox')        
        bbox = [
            int(bndbox.find('xmin').text),
            int(bndbox.find('ymin').text),
            int(bndbox.find('xmax').text),
            int(bndbox.find('ymax').text)            
        ]
        parsed["object"].append({
            "name": name,
            "difficult": difficult,
            "truncated": truncated,
            "bndbox": bbox
        })

        yolo_bbox = [
            (bbox[2] + bbox[0]) / 2 / w,    # xc
            (bbox[3] + bbox[1]) / 2 / h,    # yc
            (bbox[2] - bbox[0]) / w,        # w
            (bbox[3] - bbox[1]) / h         # h
        ]
        yolo_bbox = " ".join([str(x) for x in yolo_bbox])
        yolo_bboxs.append(f"{label_id} {yolo_bbox}")
    parsed["yolo_bbox"] = "\n".join(yolo_bboxs)
    return parsed
