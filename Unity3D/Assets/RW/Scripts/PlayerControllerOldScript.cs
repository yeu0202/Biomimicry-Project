using UnityEngine;
using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class PlayerControllerOldScript: MonoBehaviour 
{
	// 1. Declare Variables
	Thread receiveThread; //1
	UdpClient client; //2
	int port; //3

	const int arrWidth = 48;
	const int arrHeight = 27;
	public GameObject PixelPrefab;
	GameObject[,] pixelArray = new GameObject[arrHeight, arrWidth];
	int[,] pixelValues = new int [arrHeight, arrWidth];
	


	// 2. Initialize variables
	void Start () 
	{
		port = 5065; //1 

		InitUDP(); //4

		// used for debugging but i think i fixed the bug
		for (int i=0; i<arrHeight; i++){
			for(int j=0; j<arrWidth; j++){
				pixelValues[i,j] = 2550;
			}
		}

		// create tree bark cubes
		for (int i=0; i<arrHeight; i++){
			for(int j=0; j<arrWidth; j++){
				GameObject instanceCube = (GameObject)Instantiate(PixelPrefab);
				instanceCube.transform.position = this.transform.position;
				instanceCube.transform.parent = this.transform;
				instanceCube.name = "pixel " + i + ", " + j;

				// 6.7 - -9.5 = 16.2. Radius is 8.1
				// 𝑥𝑃2=𝑥𝑃1+𝑟sin𝜃; 
				// 𝑦𝑃2=𝑦𝑃1−𝑟(1−cos𝜃)
				instanceCube.transform.position = new Vector3((float)(-19.5 + j), ((float)(-1.8 - i)), 
																(float)0);

				// everything + Mathf.PI to rotate the whole thing by 180º

				pixelArray[i,j] = instanceCube;
			}
		}
	}
	
	// 3. InitUDP
	private void InitUDP()
	{
		print ("UDP Initializing");

		receiveThread = new Thread (new ThreadStart(ReceiveData)); //1 
		receiveThread.IsBackground = true; //2
		receiveThread.Start(); //3

		print ("UDP Initialized");
	}

	private void ProcessData(string text){
		int dataArrWidth = 48;
		int dataArrHeight = 27;

		string[] arrRows = text.Split(']');

		// first row
		string[] arrPixels0 = arrRows[0].Split(' ');
		
		// special case for first variable
		string[] _firstPixel0 = arrPixels0[0].Split('[');
		string firstPixel0 = _firstPixel0[_firstPixel0.Length - 1]; // get last variable
		// print("firstPixel = " + _firstPixel[0]);
		// print("firstPixel = " + firstPixel);

		string[] _tempPixel0 = firstPixel0.Split(',');
		// print("index " + "0" + ",0: " + _tempPixel0[0]);
		pixelValues[0, 0] = Convert.ToInt32(_tempPixel0[0]);

		for(int j=1; j<dataArrWidth-1; j++){ // special cases for first and last
			string[] _tempPixel2 = arrPixels0[j].Split(',');
			// print("index " + "0" + "," + j + ": " + _tempPixel2[0]);
			pixelValues[0, j] = Convert.ToInt32(_tempPixel2[0]);
		}

		// for dealing with last pixel, which has the Python brackets attached to it	
		string lastPixel0 = arrPixels0[dataArrWidth-1];
		// print("index " + "0" + ",last: " + lastPixel0);
		pixelValues[0,dataArrWidth-1] = Convert.ToInt32(lastPixel0);
		

		// rest of the cases
		for(int i=1; i<dataArrHeight; i++){
			string[] arrPixels = arrRows[i].Split(' ');
			
			// special case for first variable
			string[] _firstPixel = arrPixels[1].Split('[');
			string firstPixel = _firstPixel[_firstPixel.Length - 1]; // get last variable
			// print("firstPixel = " + _firstPixel[0]);
			// print("firstPixel = " + firstPixel);

			string[] _tempPixel = firstPixel.Split(',');
			// print("index " + i + ",0: " + _tempPixel[0]);
			pixelValues[i, 0] = Convert.ToInt32(_tempPixel[0]);

			for(int j=2; j<dataArrWidth; j++){ // special cases for first and last
				string[] _tempPixel2 = arrPixels[j].Split(',');
				// print("index " + i + "," + j + ": " + _tempPixel2[0]);
				pixelValues[i, j-1] = Convert.ToInt32(_tempPixel2[0]);
			}

			// for dealing with last pixel, which has the Python brackets attached to it	
			string lastPixel = arrPixels[dataArrWidth];
			// print("index " + i + ",last: " + lastPixel);
			pixelValues[i,dataArrWidth-1] = Convert.ToInt32(lastPixel);
		}
		// print (pixelValues);


	}

	// 4. Receive Data
	private void ReceiveData()
	{
		client = new UdpClient (port); //1
		while (true) //2
		{
			try
			{
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port); //3
				byte[] data = client.Receive(ref anyIP); //4

				string text = Encoding.UTF8.GetString(data); //5
				//print (">> " + text);
				ProcessData(text);

				// jump = true; //6

			} 
			catch(Exception e)
			{
				print (e.ToString()); //7
			}
		}
	}

	// 5. Make the Player Jump

	// public void Jump()
	// {
	// 	Player.GetComponent<Animator>().SetTrigger ("Jump"); //1
	// 	jumpSound.PlayDelayed(44100); // Play Jump Sound with a 1 second delay to match the animation
	// }
	// 6. Check for variable value, and make the Player Jump!

	void Update () 
	{
		// if(jump == true)
		// {
		// 	Jump ();
		// 	jump = false;
		// }

		
		for(int i=0; i<arrHeight; i++){
			for(int j=0; j<arrWidth; j++){
				float pixelInt = pixelValues[i, j];
				pixelInt = pixelInt/255;
				GameObject instanceCube = pixelArray[i, j];
				Vector3 cubeScale = instanceCube.transform.localScale;
				cubeScale[2] = 2+pixelInt*5;
				instanceCube.transform.localScale = cubeScale;

			}
		}
	}
}
