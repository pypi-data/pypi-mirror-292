from matplotlib import pyplot as plt
from PIL import Image


def make_plots(image_0, image_1, title_0, title_1, y, x, v, u, y_a, y_b, x_a, x_b,
               t0_fname, t1_fname, anim_filename, projection, color='black', scale=400, skip=6):
    """
    :param image_0: background image for first frame
    :param image_1: background image for second frame
    :param title_0: title for the first frame
    :param title_1: title for the second frame
    :param y: 2D array of y coordinates
    :param x: 2D array of x coordinates
    :param v: 2D array of v component of the wind
    :param u: 2D array of u component of the wind
    :param y_a: start y-index
    :param y_b: stop (exclusive) y-index
    :param x_a: start x-index
    :param x_b: stop (exclusive) x-index
    :param t0_fname: filename for the first frame
    :param t1_fname: filename for the second frame
    :param anim_filename: filename for the animated gif
    :param projection: cartopy projection object
    :param color: wind vector color
    :param scale: wind vector scale
    :param skip: wind plot skip
    """
    images = []

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax.pcolormesh(x[y_a:y_b, x_a:x_b], y[y_a:y_b, x_a:x_b], image_0, cmap='jet')
    ax.quiver(x[y_a:y_b:skip, x_a:x_b:skip], y[y_a:y_b:skip, x_a:x_b:skip], u[::skip, ::skip], v[::skip, ::skip], color=color, scale=scale)
    ax.gridlines(draw_labels=True)
    plt.title(title_0)
    # plt.show()
    fig.savefig('/Users/tomrink/'+t0_fname, dpi=300)
    images.append(Image.open('/Users/tomrink/'+t0_fname))

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax.pcolormesh(x[y_a:y_b, x_a:x_b], y[y_a:y_b, x_a:x_b], image_1, cmap='jet')
    ax.quiver(x[y_a:y_b:skip, x_a:x_b:skip], y[y_a:y_b:skip, x_a:x_b:skip], u[::skip, ::skip], v[::skip, ::skip], color=color, scale=scale)
    ax.gridlines(draw_labels=True)
    plt.title(title_1)
    # plt.show()
    fig.savefig('/Users/tomrink/'+t1_fname, dpi=300)
    images.append(Image.open('/Users/tomrink/'+t1_fname))

    images[0].save('/Users/tomrink/'+anim_filename,
                   save_all=True, append_images=images[1:], optimize=False, duration=1000, loop=0)