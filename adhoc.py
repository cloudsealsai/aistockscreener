import PyPDF2
import matplotlib.pyplot as plt


def generate_pdf():
    # Create a new PDF file
    pdf_file = open('example.pdf', 'wb')
    pdf_writer = PyPDF2.PdfFileWriter()

    # Create a Matplotlib figure and add a plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 4, 6]
    ax.plot(x, y)

    # Convert the Matplotlib figure to a PNG image and add it to the PDF
    fig.savefig('graph.png')
    with open('graph.png', 'rb') as img:
        img_obj = PyPDF2.pdf.ImageReader(img)
        page = PyPDF2.pdf.PageObject.createBlankPage(None, img_obj.getSize()[0], img_obj.getSize()[1])
        page.addImage(img_obj, 0, 0)
        pdf_writer.addPage(page)

    # Add some text to the PDF
    page = PyPDF2.pdf.PageObject.createBlankPage(None, 612, 792) # 8.5 x 11 inches (US Letter)
    page.compressContentStreams()
    page.addText("Example text added to PDF file", 100, 600)

    # Add the page with the text to the PDF
    pdf_writer.addPage(page)

    # Write the updated PDF file to disk
    pdf_writer.write(pdf_file)
    pdf_file.close()
