import os
import math
import shutil
import datetime
import configparser
import fpdf
import collections
import csv

# TODO layout tags
# TODO iterate through dictionary
# TODO create final count report


class Code():
    def __init__(self):
        self.code_dic = {}
        self.job_number = "35525"
        self.tray_max = 150

    def calculate_counts(self, fle):
        with open(fle, 'r') as f:
            next(f)
            lines = map(lambda x: x.replace('"', '').strip('\n'), f.readlines())
            self.code_dic = collections.Counter(lines)

class Tag():
    def __init__(self, code, count, jobnum, tray_max):
        self.code = code
        self.count = count
        self.jobnum = jobnum
        self.tray_max = tray_max
        self.leftover = count % tray_max
        self.trays = math.floor(count / tray_max) + 1

    def write_tag(self, pdf, tag_obj, offset=0):
        y_offset = math.floor(offset/2) * 2
        x_offset = (offset % 2) * 3.25

        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(1 + x_offset, .5 + y_offset)
        # pdf.cell(3.25, 2, "", border=0)

        pdf.set_y(pdf.get_y() + .1)
        pdf.set_x(pdf.get_x() + x_offset)

        pdf.cell(3.25, .26, self.jobnum, align='C')
        pdf.set_y(pdf.get_y() + .26)
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(3.25, .42, "Bindery 1", align='C')
        pdf.set_y(pdf.get_y() + .42)
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.set_font('Arial', 'B', 32)
        pdf.cell(3.25, .4, self.code, align='C')
        pdf.set_font('Arial', 'B', 18)
        pdf.set_y(pdf.get_y() + .4)
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.cell(3.25, .4, "Tray {} of {}".format(offset + 1, tag_obj.trays), align='C')
        pdf.set_y(pdf.get_y() + .4)
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(3.25, .2, "Tray total: {count}    {code} total: {count}".format(count=self.tray_max,
                                                                                 code=self.code),
                 align='C')


def initialize_new_path(pth):
    if os.path.exists(pth):
        shutil.rmtree(pth)
        os.makedirs(pth)
    else:
        os.makedirs(pth)


def process_tags():
    savepath = os.path.join(os.curdir, 'tags')
    initialize_new_path(savepath)
    files = [f for f in os.listdir(os.curdir) 
             if f[-3:].upper() == 'TXT']

    for f in files:
        code = Code()
        code.calculate_counts(f)

        for print_code, count in code.code_dic.items():

            job_tag = Tag(print_code, count, code.job_number, code.tray_max)

            print(job_tag.__dict__)

            if job_tag.trays == 1:
                pdf = fpdf.FPDF(orientation = 'P', unit = 'in', format='Letter')
                pdf.set_margins(left=1, right=1, top=.5)
                pdf.add_page()
                job_tag.write_tag(pdf, job_tag)
                pdf.output(os.path.join(savepath, '{}.pdf'.format(print_code)), 'F')
            else:
                pdf = fpdf.FPDF(orientation='P', unit='in', format='Letter')
                pdf.set_margins(left=1, right=1, top=.5)
                pdf.add_page()
                for tag in range(job_tag.trays):
                    job_tag.write_tag(pdf, job_tag, tag)
                pdf.output(os.path.join(savepath, '{}.pdf'.format(print_code)), 'F')



def main():
    process_tags()

if __name__ == '__main__':
    main()
