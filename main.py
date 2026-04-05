import argparse
import traceback

parser = argparse.ArgumentParser(
    description='This program converts a bitmap to colored grids in SVG.',
    epilog=(
        'Example: python main.py input.png output.svg\n'
        'To preserve transparency, add --preserve_alpha.\n'
        'If you encounter an error or have a suggestion, please open an issue:\n'
        'https://github.com/bitmap_to_colored_grids_svg/issues'
        '\n If you find this tool useful, consider giving it a star on GitHub!\n'
        'https://github.com/bitmap_to_colored_grids_svg/'
    ))

parser.add_argument('input_file', 
                    type=str, 
                    help='The path to the input bitmap file, supports common bitmap formats like PNG, JPEG, etc.')
parser.add_argument('-o', '--output_file', 
                    type=str, 
                    nargs='?',
                    default='output.svg',
                    help='The path to the output SVG file, default is output.svg if not provided.',)
parser.add_argument('--preserve_alpha',
                    action='store_true',
                    help='Preserve the alpha channel (transparency) in the output SVG. When enabled, overlap must be 0.')
parser.add_argument('--pixel_size',
                    type=float, 
                    nargs='?', 
                    default=1.0, 
                    help='The size of each pixel in the output SVG in px. Default is 1.0.')
parser.add_argument('--overlap',
                    type=float, 
                    nargs='?', 
                    default=None, 
                    help='The overlap between adjacent pixels, in px, used to help prevent visible gaps. Must be smaller than pixel_size. If omitted, the default is 10%% of pixel_size.')
parser.add_argument('--outline',
                    action='store_true',
                    help='Add thin colored outlines along pixel edges to help eliminate rendering issues at the seams.')

args = parser.parse_args()

if args.pixel_size <= 0:
    parser.error('pixel_size must be greater than 0. Please retry with a positive pixel_size.')

if args.overlap is None:
    args.overlap = args.pixel_size * 0.1

if args.overlap < 0:
    parser.error('overlap must be greater than or equal to 0. Please retry with a non-negative overlap.')

if args.overlap >= args.pixel_size:
    parser.error('overlap must be smaller than pixel_size. Please retry with a smaller overlap or larger pixel_size.')

if args.preserve_alpha and args.overlap != 0:
    parser.error('overlap must be 0 when preserve_alpha is True. Please retry with --overlap 0 or disable preserve_alpha.')

if args.preserve_alpha and args.outline:
    parser.error('outline is not compatible with preserve_alpha. Please retry without --outline or disable preserve_alpha.')

from PIL import Image
import svgwrite

def main(input_file, output_file, preserve_alpha, pixel_size, overlap):
    # Load the bitmap image
    image = Image.open(input_file)
    image = image.convert('RGBA')  # Ensure the image is in RGBA format, since some image formats may not originally have an alpha channel
    width, height = image.size

    # Create an SVG drawing
    dwg = svgwrite.Drawing(output_file, size=(width * pixel_size, height * pixel_size))

    # Iterate through each pixel in the bitmap image
    for x in range(width):
        for y in range(height):
            r, g, b, a = image.getpixel((x, y))  # Get the RGBA values
            if not preserve_alpha:
                a = 255  # override alpha to 255 (fully opaque)
            color = svgwrite.rgb(r, g, b, 'RGB')
            opacity = a / 255

            # viewport is set, so there is no need to worry about going out of bounds
            dwg.add(dwg.rect(
                insert=(x * pixel_size, y * pixel_size), 
                size=(pixel_size + overlap, pixel_size + overlap), 
                fill=color,
                fill_opacity=opacity))
            
    if args.outline:
        for x in range(width):
            for y in range(height):
                r, g, b, _ = image.getpixel((x, y))  # Get the RGBA values
                color = svgwrite.rgb(r, g, b, 'RGB')

                dwg.add(dwg.line(
                    start=((x + 1) * pixel_size, y * pixel_size), 
                    end=((x + 1) * pixel_size, (y + 1) * pixel_size), 
                    stroke=color,
                    stroke_width=0.001 * pixel_size))
                dwg.add(dwg.line(
                    start=(x * pixel_size, (y + 1) * pixel_size), 
                    end=((x + 1) * pixel_size, (y + 1) * pixel_size), 
                    stroke=color,
                    stroke_width=0.001 * pixel_size))

    # Save the SVG file
    dwg.save()

if __name__ == '__main__':
    try:
        main(args.input_file, args.output_file, args.preserve_alpha, args.pixel_size, args.overlap)
        print(f'Successfully converted {args.input_file} into colored grids SVG {args.output_file}'
              '\nIf you find this tool useful, consider giving it a star on GitHub!'
              '\nhttps://github.com/bitmap_to_colored_grids_svg/')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}'
              '\033[5;31m' # Start red colored text
              f'\n{traceback.format_exc()}'
              '\033[0m' # End red colored text
              'Please check the input file path and ensure it is a valid bitmap image.'
              '\nIf the problem persists, consider checking or opening an issue on GitHub with'
              '\n- steps to reproduce, and'
              '\n- the error messages above:'
              '\nhttps://github.com/bitmap_to_colored_grids_svg/issues')