# coding=utf-8
import errno
import logging
import os

from dicom import read_file
from dicom.tag import TupleTag

from dcmlib.dicom_ import get_tag_value, monkey_patch_dicom, \
    make_up_file_dataset

# 猴子补丁
monkey_patch_dicom()

logger = logging.getLogger('desensitize')

SENSITIVE_TAGS = [
    (0x0008, 0x0090),  # Referring Physician's Name
    (0x0008, 0x0080),  # Institution Name
    (0x0008, 0x0081),  # Institution Address
    (0x0008, 0x0082),  # Institution Sequence Number
    (0x0008, 0x0090),  # Referring Physician's name
    (0x0008, 0x0092),  # Referring Physician Address
    (0x0008, 0x0094),  # Referring Physician's Phone
    (0x0008, 0x1010),  # Station name
    (0x0008, 0x1040),  # Institutional Department Name
    (0x0008, 0x1048),  # Physician(s) of Record
    (0x0008, 0x1049),  # Physician(s) of Record Identification
    (0x0008, 0x1050),  # Performing Physician's Name
    (0x0008, 0x1060),  # Reading Physicians Name
    (0x0008, 0x1070),  # Operator's Name
    (0x0010, 0x0010),  # Patient's Name
    (0x0010, 0x1040),  # Patient's Address
    (0x0010, 0x2154),  # Patient's Telephone Numbers
    (0x0019, 0x161b),  # TODO(weidwonder): need add description
    (0x0032, 0x1032),  # Requesting Physician
    (0x0033, 0x1013),  # [Patient's Name]
    (0x0010, 0x0050),  # Patient Insurance Plan Code Sequence
    (0x0038, 0x0400),  # Patient Institution Residence
]


def desensitize(ds, sensitive_tags=None, img_ds=True,
                img_ds_area=(None, None, None, None)):
    """ 脱敏函数
    :param ds: Dataset 待脱敏Dataset对象
    :param sensitive_tags: list 敏感标签
    :param img_ds: bool 是否进行图像脱敏
    :param img_ds_area: tuple 图像脱敏区域(x_min, x_max, y_min, y_max) None 表示不限
    :return: Dataset 已脱敏对象
    """
    if not sensitive_tags:
        sensitive_tags = SENSITIVE_TAGS
        # 标签脱敏
    for tag in sensitive_tags:
        tag = TupleTag(tag)
        logger.debug('Desensitizing %s tag.' % tag)
        ds.pop(tag, None)
    return ds


def desensitize_file(path, out_path=None, **kws):
    """ 对文件进行脱敏
    :param path: str 文件路径 
    :param out_path: str 输出路径
    """
    if not out_path:
        out_path = path
    ds = read_file(path, force=True)
    if is_desensitized(ds) and path == out_path:
        return
    ds = desensitize(ds, **kws)
    ds = make_up_file_dataset(out_path, ds)
    ds.save_as(out_path)


def desensitize_dir(path, out_path=None, **kws):
    """
    对文件夹进行脱敏
    :param path: 源文件夹路径
    :param out_path: 输出文件夹路径, 无则直接覆盖当前文件夹
    :param kws:
    :return:
    """
    out_path = out_path or path
    failed_list = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, path)
            outfile_path = os.path.join(out_path, rel_path)
            mkdir_recursive(os.path.split(outfile_path)[0])
            try:
                desensitize_file(file_path, outfile_path)
            except:
                import traceback
                traceback.print_exc()
                failed_list.append(file_path)
    return failed_list


def is_desensitized(d):
    """
    文件是否脱敏过
    :param d: Dataset 待检查影像
    :return: bool
    """
    #print(not any(get_tag_value(d, *tag) for tag in SENSITIVE_TAGS))
    return not any(get_tag_value(d, *tag) for tag in SENSITIVE_TAGS)

def is_not_desensitized(dir):
    file_list = [os.path.join(dir,i) for i in os.listdir(dir)]
    bool_list = []
    for d in file_list:
        ds = read_file(d)
        bool_ = str(not any(get_tag_value(ds, *tag) for tag in SENSITIVE_TAGS))
        if bool_ not in bool_list:
            bool_list.append(bool_)
    if len(bool_list) == 1:
        return True
    else:
        return False
    #return not any(get_tag_value(ds, *tag) for tag in SENSITIVE_TAGS)


def mkdir_recursive(path, mode=0777):
    """
    等同于 mkdir -p <path>
    且如果文件夹存在不报错
    :param path: str 目录路径
    :param mode: int 目录权限
    """
    try:
        os.makedirs(path, mode=mode)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':
    root = '/media/tx-deepocean/Data/DICOMS/test/07047952/1.2.840.113619.2.55.3.1690327908.79.1536922796.792.4'
    file_list = [os.path.join(root,i) for i in os.listdir(root)]
    for file_ in file_list:
        print file_
        print is_not_desensitized(file_)
