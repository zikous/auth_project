import asyncio
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
import threading
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.graphics.imaging import BitmapDecoder, BitmapPixelFormat, BitmapAlphaMode, SoftwareBitmap
from winrt.windows.storage import StorageFile, FileAccessMode

class OCRInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Image Text Extractor")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Image selection section
        ttk.Label(main_frame, text="Select Image:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.image_path_var = tk.StringVar()
        self.path_entry = ttk.Entry(main_frame, textvariable=self.image_path_var, width=50)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 5))
        
        self.browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_image)
        self.browse_btn.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Extract Text", command=self.process_image)
        self.process_btn.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(40, 0))
        self.progress.grid_remove()  # Hide initially
        
        # Results section
        ttk.Label(main_frame, text="Extracted Text:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        
        # Text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(main_frame, width=70, height=20, wrap=tk.WORD)
        self.text_area.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(30, 0))
        
        # Image preview frame
        self.preview_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="5")
        self.preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.image_label = ttk.Label(self.preview_frame, text="No image selected")
        self.image_label.pack()
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path_var.set(file_path)
            self.show_preview(file_path)
    
    def show_preview(self, image_path):
        try:
            # Open and resize image for preview
            image = Image.open(image_path)
            # Resize to fit preview area (max 300x200)
            image.thumbnail((300, 200), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.image_label.configure(text=f"Preview error: {str(e)}", image="")
            self.image_label.image = None
    
    async def perform_ocr(self, image_path):
        try:
            # Convert path to proper format for Windows Runtime
            import os
            full_path = os.path.abspath(image_path)
            
            file = await StorageFile.get_file_from_path_async(full_path)
            stream = await file.open_async(FileAccessMode.READ)
            decoder = await BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            
            if (bitmap.bitmap_pixel_format != BitmapPixelFormat.BGRA8 or
                bitmap.bitmap_alpha_mode != BitmapAlphaMode.PREMULTIPLIED):
                bitmap = SoftwareBitmap.convert(bitmap, BitmapPixelFormat.BGRA8, BitmapAlphaMode.PREMULTIPLIED)
            
            ocr_engine = OcrEngine.try_create_from_user_profile_languages()
            if not ocr_engine:
                raise Exception("No OCR engine available for current language")
                
            result = await ocr_engine.recognize_async(bitmap)
            
            extracted_text = []
            for line in result.lines:
                extracted_text.append(line.text)
            
            return "\n".join(extracted_text)
            
        except Exception as e:
            raise Exception(f"OCR Error: {str(e)}")
    
    def process_image(self):
        image_path = self.image_path_var.get().strip()
        
        if not image_path:
            messagebox.showerror("Error", "Please select an image file first.")
            return
        
        # Clear previous results
        self.text_area.delete(1.0, tk.END)
        
        # Show progress bar and disable button
        self.progress.grid()
        self.progress.start()
        self.process_btn.configure(state='disabled')
        
        # Run OCR in a separate thread
        def run_ocr():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(self.perform_ocr(image_path))
                
                # Update UI in main thread
                self.root.after(0, self.on_ocr_complete, result, None)
                
            except Exception as e:
                self.root.after(0, self.on_ocr_complete, None, str(e))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_ocr, daemon=True)
        thread.start()
    
    def on_ocr_complete(self, result, error):
        # Hide progress bar and enable button
        self.progress.stop()
        self.progress.grid_remove()
        self.process_btn.configure(state='normal')
        
        if error:
            messagebox.showerror("Error", f"Failed to extract text:\n{error}")
        elif result:
            self.text_area.insert(1.0, result)
            if not result.strip():
                self.text_area.insert(1.0, "No text found in the image.")
        else:
            self.text_area.insert(1.0, "No text found in the image.")

def main():
    root = tk.Tk()
    app = OCRInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()