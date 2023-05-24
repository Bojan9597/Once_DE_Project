using System.Text.RegularExpressions;
using Emgu.CV;
using Emgu.CV.Structure;
using OpenTK.Graphics.OpenGL;
using Emgu.CV.Util;

namespace ClickableEvents
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

            // Start a timer to update the panel with new frames
            System.Windows.Forms.Timer timer = new System.Windows.Forms.Timer();
            timer.Interval = 1; // Set the interval in milliseconds
            timer.Tick += new EventHandler(UpdateFrame);
            Console.WriteLine("adsadf");
            timer.Start();
        }

        private void UpdateFrame(object sender, EventArgs e)
        {
            // Capture a frame from the camera
            Mat frame = new Mat();
            capture.Read(frame);

            // If the frame is not empty, display it on the panel
            if (!frame.IsEmpty)
            {
                Bitmap bitmap = frame.ToBitmap();
                // Convert the frame to a bitmap and display it on the panel
                panel1.BackgroundImage = bitmap;
            }
        }

    }
}