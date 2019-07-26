import os
import math
import shutil
import fpdf
import collections
import time

# TODO Make a single file for all tags
# TODO Check code for condition where code qty is the same as tray max, or evenly divisible

class Code:
    def __init__(self):
        self.code_dic = {}
        self.job_number = "35525"
        self.tray_max = 150

    def calculate_counts(self, fle):
        with open(fle, 'r') as f:
            next(f)
            lines = map(lambda x: x.replace('"', '').strip('\n'), f.readlines())
            self.code_dic = collections.Counter(lines)

    def ask_questions(self):
        ans = input("Enter job number: ")
        if ans == "":
            print("Must enter job number, restart program after exit")
            time.sleep(3.5)
            exit()
        self.job_number = ans

        ans = int(input("Enter max pieces per tray: "))
        if not isinstance(ans, int) or int(ans) <= 0:
            print("Tray count must be a number and greater than 0")
            time.sleep(3.5)
            exit()
        self.tray_max = ans


class Tag:
    def __init__(self, code, count, jobnum, tray_max):
        self.code = code
        self.count = count
        self.jobnum = jobnum
        self.tray_max = tray_max
        self.leftover = count % tray_max
        self.trays = math.floor(count / tray_max) + 1

    def write_tag(self, pdf, tag_obj, tag_number, offset=0):
        if tag_number % 10 == 0 and tag_number != 0:
            pdf.add_page()
        y_offset = math.floor(offset/2) * 2
        x_offset = (offset % 2) * 3.25

        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(1 + x_offset, .5 + y_offset)
        pdf.cell(3.25, 2, "", border=0)

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
        pdf.cell(3.25, .4, "Tray {} of {}".format(tag_number + 1, tag_obj.trays), align='C')
        pdf.set_y(pdf.get_y() + .4)
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.set_font('Arial', 'B', 12)

        if tag_number + 1 == tag_obj.trays:
            pdf.cell(3.25, .2, "Tray total: {count}    {code} total: {total:,}".format(count=self.leftover,
                                                                                       code=self.code,
                                                                                       total=self.count),
                     align='C')
        else:
            pdf.cell(3.25, .2, "Tray total: {count}    {code} total: {total:,}".format(count=self.tray_max,
                                                                                       code=self.code,
                                                                                       total=self.count),
                     align='C')


def initialize_new_path(pth):
    if os.path.exists(pth):
        shutil.rmtree(pth)
        os.makedirs(pth)
    else:
        os.makedirs(pth)


def process_tags():
    save_path = os.path.join(os.curdir, 'tags')
    initialize_new_path(save_path)
    files = [f for f in os.listdir(os.curdir) 
             if f[-3:].upper() == 'TXT' and f != 'Count Report.txt']

    for f in files:
        code = Code()
        code.ask_questions()
        code.calculate_counts(f)

        with open('Count Report.txt', 'w+') as r:
            r.write("Job #: {}\nMax {} per tray\n\n{:<10}{:>10}{:>8}\n".format(code.job_number,
                                                                               code.tray_max,
                                                                               'Code',
                                                                               'Count',
                                                                               'Trays'))

            for print_code, count in code.code_dic.items():

                job_tag = Tag(print_code, count, code.job_number, code.tray_max)

                print(job_tag.__dict__)

                if job_tag.trays == 1:
                    pdf = fpdf.FPDF('P', 'in', (8.5, 11))
                    pdf.set_margins(left=1, right=1, top=.5)
                    pdf.add_page()
                    job_tag.write_tag(pdf, job_tag, 0, 0)
                    pdf.output(os.path.join(save_path, '{}.pdf'.format(print_code)), 'F')
                else:
                    pdf = fpdf.FPDF('P', 'in', (8.5, 11))
                    pdf.set_auto_page_break(False)
                    pdf.set_margins(left=1, right=1, top=.5)
                    pdf.add_page()
                    for tag_number in range(job_tag.trays):
                        offset = tag_number % 10
                        job_tag.write_tag(pdf, job_tag, tag_number, offset)
                    pdf.output(os.path.join(save_path, '{}.pdf'.format(print_code)), 'F')

                r.write("{:<10}{:>10,}{:>8,}\n".format(job_tag.code, job_tag.count, job_tag.trays))


def main():
    process_tags()


if __name__ == '__main__':
    main()
