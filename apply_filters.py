# Filtros e operações com OpenCV
import cv2
import numpy as np

def apply_box_blur(img, ksize=5):
    return cv2.blur(img, (ksize, ksize))

def apply_gaussian_blur(img, ksize=5):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)

def apply_median_blur(img, ksize=5):
    return cv2.medianBlur(img, ksize)

def apply_bilateral_filter(img, d=9, sigmaColor=75, sigmaSpace=75):
    return cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)

def apply_sharpen(img):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def apply_laplacian(img):
    lap = cv2.Laplacian(img, cv2.CV_64F)
    lap = cv2.convertScaleAbs(lap)
    return lap

def apply_sobel(img, dx=1, dy=0, ksize=3):
    sobel = cv2.Sobel(img, cv2.CV_64F, dx, dy, ksize=ksize)
    sobel = cv2.convertScaleAbs(sobel)
    return sobel

def apply_canny(img, threshold1=100, threshold2=200):
    # Canny espera imagem em escala de cinza
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(img, threshold1, threshold2)

def apply_emboss(img):
    kernel = np.array([[-2, -1, 0],
                       [-1, 1, 1],
                       [0, 1, 2]])
    embossed = cv2.filter2D(img, -1, kernel)
    embossed = cv2.convertScaleAbs(embossed)
    return embossed

def apply_sepia(img):
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, kernel)
    sepia = np.clip(sepia, 0, 255)
    return sepia.astype(np.uint8)

def select_channel(img, channel):
    # channel: 'R', 'G', 'B'
    b, g, r = cv2.split(img)
    zeros = np.zeros_like(b)
    if channel == 'R':
        return cv2.merge([zeros, zeros, r])
    elif channel == 'G':
        return cv2.merge([zeros, g, zeros])
    elif channel == 'B':
        return cv2.merge([b, zeros, zeros])
    else:
        return img


def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


filters = {
    "Box Blur": apply_box_blur,
    "Gaussian Blur": apply_gaussian_blur,
    "Median Blur": apply_median_blur,
    "Bilateral Filter": apply_bilateral_filter,
    "Sharpen": apply_sharpen,
    "Laplacian": apply_laplacian,
    "Sobel X": lambda img: apply_sobel(img, dx=1, dy=0, ksize=3),
    "Sobel Y": lambda img: apply_sobel(img, dx=0, dy=1, ksize=3),
    "Canny Edges": apply_canny,
    "Emboss": apply_emboss,
    "Sepia": apply_sepia,
    "Red Channel": lambda img: select_channel(img, 'R'),
    "Green Channel": lambda img: select_channel(img, 'G'),
    "Blue Channel": lambda img: select_channel(img, 'B'),
    "Grayscale": to_grayscale
}