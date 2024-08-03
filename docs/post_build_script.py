import shutil
import os
import json

# Figure out if we are in the `docs` directory or the root directory
if os.path.exists('index.html'):
    print("Found index.html in current directory, assuming we are in the root directory")
else:
    print("In the root directory, changing to docs directory")
    os.chdir('docs')
    if not os.path.exists('index.html'):
        raise FileNotFoundError("Could not find index.html in the root directory or the docs directory. Are you in the `website` branch?")

# Path to your custom index.html
custom_index = 'index.html'
# Path to your images folder
images_folder = 'images'
# Path to the built book (adjust as needed)
built_book = '_build/html'
# Path to the images destination in the built book
built_images = os.path.join(built_book, 'images')

# Copy the custom index.html to the built book directory
shutil.copy2(custom_index, os.path.join(built_book, 'index.html'))
print(f"Copied custom index.html to {built_book}")


def rm_and_copy(src, dst):
    if os.path.exists(dst):
        # If the directory exists, remove it first to ensure a clean copy
        shutil.rmtree(dst)
    # Copy the entire directory
    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

# Copy the entire images directory
rm_and_copy('images', built_images)

# Copy the vendor directory
rm_and_copy('vendor', os.path.join(built_book, 'vendor'))

# Copy the css directory
rm_and_copy('css', os.path.join(built_book, 'css'))

# Copy the assets directory
rm_and_copy('assets', os.path.join(built_book, 'assets'))

print("Post-build process completed successfully!")