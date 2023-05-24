using Emgu.CV;
using Emgu.CV.Structure;
using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace ClickableEventsFromCamera
{
    public partial class Form1 : Form
    {
        private VideoCapture capture;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // Create a VideoCapture object for the default camera
            capture = new VideoCapture();

            // Start a timer to update the videoBox with new frames
            System.Windows.Forms.Timer timer = new System.Windows.Forms.Timer();
            timer.Interval = 1; // Set the interval in milliseconds
            timer.Tick += new EventHandler(UpdateFrame);
            timer.Start();
        }

        private void UpdateFrame(object sender, EventArgs e)
        {
            // Capture a frame from the camera
            Mat frame = new Mat();
            capture.Read(frame);

            // If the frame is not empty, display it on the videoBox
            if (!frame.IsEmpty)
            {
                // Convert the frame to a Bitmap for display
                Bitmap bitmap = frame.ToBitmap();

                // Set the videoBox picture box's image with the converted frame
                videoBox.Image = bitmap;

                // Set the picture box's size mode to zoom to fit the entire image
                videoBox.SizeMode = PictureBoxSizeMode.Zoom;
            }
        }

        private void videoBox_Click(object sender, EventArgs e)
        {
            // Get the clicked position relative to the picture box
            MouseEventArgs me = (MouseEventArgs)e;
            Point clickedPoint = me.Location;

            // Calculate the position relative to the image (assuming Zoom mode)
            double ratioX = (double)videoBox.Image.Width / videoBox.Width;
            double ratioY = (double)videoBox.Image.Height / videoBox.Height;
            int imageX = (int)(clickedPoint.X * ratioX);
            int imageY = (int)(clickedPoint.Y * ratioY);

            // Calculate the position relative to the top-left corner of the image box
            int boxX = clickedPoint.X;
            int boxY = clickedPoint.Y;

            // Write the coordinates to a text file
            string coordinates = $"Image Box: ({boxX},{boxY}) - Image: ({imageX},{imageY})";
            File.AppendAllText("C:\\Users\\bojan\\Desktop\\Once_DE_Project\\Once_DE_Project\\CsharpModules\\LoadImagesFromCamAndMenageClickableEvents\\coordinates.txt", coordinates + "\n");
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            // Release the camera
            if (capture != null)
            {
                capture.Dispose();
            }
        }
    }
}
