import shutil
from tqdm.auto import tqdm
from pathlib import Path

from jcopvision.io.dataset import read_pascal_xml


def convert_pascal_to_yolo(source_dir, out_dir, classes, exclude_classes=[], exclude_truncated=True, exclude_difficult=True, copy_source_images=True):
    shutil_op = shutil.copy if copy_source_images else shutil.move

    source_dir = Path(source_dir)
    out_dir = Path(out_dir)

    image_dir = out_dir / "images"
    image_dir.mkdir(exist_ok=True, parents=True)
    label_dir = out_dir / "labels"
    label_dir.mkdir(exist_ok=True, parents=True)

    source_xmls = sorted(Path(source_dir).glob("*.xml"))
    for xml_file in tqdm(source_xmls):
        data = read_pascal_xml(xml_file, classes, exclude_classes, exclude_truncated, exclude_difficult)
        if "yolo_bbox" in data:
            shutil_op(source_dir / data["filename"], image_dir / data["filename"])
            with open(label_dir / xml_file.with_suffix(".txt").name, "w") as f:
                f.write(data["yolo_bbox"])


def create_yolo_data_yaml(data_path, classes, output_name="data.yaml"):
    data_path = Path(data_path)
    paths = [f"path: ../{data_path}"] + [f"{path.name}: {path.name}/images/" for path in data_path.iterdir() if path.name in ["train", "val", "test"]]
    dataset_info = "\n".join(paths)

    classes_str = "\n".join([f"  {i}: {label}" for i, label in enumerate(classes)])
    classes_info = f"nc: {len(classes)}\nnames:\n{classes_str}"
    
    with open(data_path / output_name, "w") as f:
        f.write("# Dataset Info\n")
        f.write(dataset_info)

        f.write("\n\n# Classes Info\n")
        f.write(classes_info)
