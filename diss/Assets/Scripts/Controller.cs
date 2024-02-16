using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Controller : MonoBehaviour
{
    public int Rows, Cols;
    public GameObject Piston;
    public GameObject[,] Pistons;
    public float movementSpeed = 100.0f;

    private float xOffset = 17.32f;
    private float zOffset = 20.0f;

    void Start()
    {
        Pistons = new GameObject[Rows,Cols];
        
        for (int i = 0; i < Rows; i++)
        {
            for (int j = 0; j < Cols; j++)
            {
                Vector3 position = new Vector3(0, 0, i * zOffset);

                position.x += j * xOffset;

                if(j % 2 != 0)
                    position.z += zOffset / 2;
                
                GameObject obj = Instantiate(Piston, position, Quaternion.identity);
                Pistons[i,j] = obj;
            }
        }
    }

    void Update()
    {
        foreach (var p in Pistons)
        {
            // Calculate the distance from the current position to height 0
            float distanceToZero = 0 - p.transform.position.y;

            // Calculate the movement towards height 0 based on the distance and movement speed
            float verticalMovement = Mathf.Sign(distanceToZero) * Mathf.Min(Mathf.Abs(distanceToZero), movementSpeed * Time.deltaTime);

            // Calculate the new position
            Vector3 newPosition = p.transform.position + Vector3.up * verticalMovement;

            // Update the position of the piston
            p.transform.position = newPosition;
        }
    }
}
