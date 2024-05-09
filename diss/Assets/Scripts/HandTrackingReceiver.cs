using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using System;
using System.Text;
using System.Collections;

public class HandTrackingReceiver : MonoBehaviour
{
    // IP address of the Python script
    public string ipAddress = "127.0.0.1";
    // Port to listen on
    public int port = 2525;  
    public Controller controller;
    public float movementMultiplier = 1.0f;
    public float minVerticalMovement = 10.0f;
    public float maxVerticalMovement = 10.0f;

    private GameObject[,] objectsArray;
    private TcpListener listener;
    private TcpClient client;
    private NetworkStream stream;

    private bool initialDataRecieved = false;
    private float artificalLatency = 0;

    private void Start()
    {
        movementMultiplier *= 1000.0f;
        listener = new TcpListener(IPAddress.Parse(ipAddress), port);
        listener.Start();

        client = listener.AcceptTcpClient();
        stream = client.GetStream();

    }

    private void Update()
    {
        if (stream.DataAvailable)
        {
            if(!initialDataRecieved)
            {
                byte[] dataBuffer = new byte[4];
                stream.Read(dataBuffer, 0, dataBuffer.Length);
                artificalLatency = BitConverter.ToInt32(dataBuffer, 0) / 1000.0f;
                initialDataRecieved = true;
                SendAcknowledgment();
            }
            else
            {
                // 4 bytes for float (distance), 4 bytes for int (x), 4 bytes for int (y)
                byte[] dataBuffer = new byte[12]; 
                stream.Read(dataBuffer, 0, dataBuffer.Length);

                using MemoryStream memoryStream = new MemoryStream(dataBuffer);
                    ProcessData(dataBuffer);
            }
            
        }
    }

    private void ProcessData(byte[] dataBuffer)
    {
        float distance = BitConverter.ToSingle(dataBuffer, 0);
        int screen_x = BitConverter.ToInt32(dataBuffer, 4);
        int screen_y = BitConverter.ToInt32(dataBuffer, 8);

        objectsArray = controller.Pistons;
        float verticalMovement;

        if (distance > 0.125)
            verticalMovement = distance;
        else
            verticalMovement = distance * -1.0f;

        // Apply the movement to the object in the 2D array
        GameObject obj = objectsArray[screen_x, screen_y];
        if (obj != null)
        {
            // Calculate the new position based on the vertical movement
            Vector3 newPosition = obj.transform.position + Vector3.up * verticalMovement * movementMultiplier * Time.deltaTime;
            newPosition.y = Mathf.Clamp(newPosition.y, minVerticalMovement, maxVerticalMovement);

            // Update the position of the object
            obj.transform.position = newPosition;
        }

        SendAcknowledgment();
    }

    private void SendAcknowledgment()
    {
        byte[] data = Encoding.UTF8.GetBytes("A");
        client.GetStream().BeginWrite(data, 0, data.Length, null, null);
    }

    private void OnDestroy()
    {
        stream.Close();
        client.Close();
        listener.Stop();
    }
}