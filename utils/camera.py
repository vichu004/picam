import subprocess
import os
import logging
import time

logger = logging.getLogger(__name__)

class PiCamera:
    def __init__(self):
        self.output_dir = "uploads"
        os.makedirs(self.output_dir, exist_ok=True)

    def capture(self):
        """
        Captures an image using libcamera-still (standard on Bookworm).
        Returns the path to the captured image.
        """
        filename = f"scan_{int(time.time())}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        # Command for Raspberry Pi OS (Bookworm) with Module 3
        # -t 1: Timeout 1ms (immediate capture after startup)
        # --width 1920 --height 1080: High res for OCR
        # -o: Output file
        # --nopreview: Don't show HDMI preview
        # --autofocus-mode: auto (Module 3 has AF)
        
        # Try 'rpicam-still' first (new alias), then 'libcamera-still'
        commands = [
            ["rpicam-still", "-t", "1000", "-o", filepath, "--width", "1920", "--height", "1080", "--nopreview", "--autofocus-mode", "auto"],
            ["libcamera-still", "-t", "1000", "-o", filepath, "--width", "1920", "--height", "1080", "--nopreview", "--autofocus-mode", "auto"]
        ]

        for cmd in commands:
            try:
                logger.info(f"Attempting capture with: {' '.join(cmd)}")
                # Run command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if os.path.exists(filepath):
                    logger.info("Capture successful")
                    return filepath
            except subprocess.CalledProcessError as e:
                logger.warning(f"Command failed: {e.stderr}")
            except FileNotFoundError:
                logger.warning(f"Command not found: {cmd[0]}")
        
        # Fallback for testing on non-Pi (Windows/Mac)
        if os.name == 'nt' or not os.path.exists("/usr/bin/rpicam-still"):
            logger.info("Not on Pi or camera failed, using dummy image")
            return self._create_dummy_image(filepath)

        raise Exception("Could not capture image with Pi Camera")

    def _create_dummy_image(self, filepath):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1920, 1080), color='gray')
        d = ImageDraw.Draw(img)
        d.text((50, 50), "Dummy Capture (Camera Not Found)", fill=(255, 255, 255))
        img.save(filepath)
        return filepath

camera = PiCamera()
