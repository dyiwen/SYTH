#!/usr/bin/env python
# encoding: utf-8

import os, dicom


class Dicomfilter:
    @staticmethod
    def iterpath(path):
        for rootpath, folder, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(rootpath, filename)
                try:
                    dr = dicom.read_file(filepath, force=True)
                    yield filepath, dr
                except:
                    pass

    @staticmethod
    def remove(filepath):
        os.remove(filepath)

    class DR:
        """
        过滤X-RAY文件
        """

        def __init__(self, path, part='CHEST', pos='PA'):
            self.part = part
            self.pos = pos
            self.valid = False
            for filepath, dr in Dicomfilter.iterpath(path):
                self.c_body_position(getattr(dr, 'BodyPartExamined', ''))
                self.c_view_position(getattr(dr, 'ViewPosition', ''))
                if not self.vaild:
                    Dicomfilter.remove(filepath)

        def c_body_part(self, BodyPartExamined):
            self.vaild = self.part in str(BodyPartExamined).upper()

        def c_view_position(self, ViewPosition):
            self.vaild = self.pos == str(ViewPosition).upper()

    class CT:
        """
        过滤CT文件
        """

        def __init__(self, path, thicknessList=['0.5','0.625','1','1.25']):
            self.thicknessList = thicknessList
            self.seriesdict = {}
            self.keyLength = {}
            self.vaild = False

            try:
                for filepath, dr in Dicomfilter.iterpath(path): #读dicom file
                    self.c_slice_thickness(getattr(dr, 'SliceThickness', '')) #验证层厚
                    if not self.vaild:
                        Dicomfilter.remove(filepath) #  thin image left
                        continue
                    self.c_series(filepath, getattr(dr, 'SeriesNumber', ''))

                if len(self.seriesdict.keys()) >= 2:
                    for key in self.seriesdict.keys():
                        self.keyLength[key] = len(self.seriesdict.get(key))

                    maxkey = max(self.keyLength.items(), key=lambda x: x[1])[0]
                    for key in self.seriesdict.keys():
                        if maxkey <> key:

                            [Dicomfilter.remove(filepath) for filepath in self.seriesdict.get(key)]        
            except:
                print "Error while Filtering..."

        def c_slice_thickness(self, SliceThickness):
            self.vaild = any(thickness in str(SliceThickness).strip('0') for thickness in self.thicknessList)

        def c_series(self, filepath, SeriesNumber):
            if self.seriesdict.has_key(SeriesNumber):
                self.seriesdict[SeriesNumber].append(filepath)
            else:
                self.seriesdict[SeriesNumber] = [filepath]

