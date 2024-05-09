using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BallMovement : MonoBehaviour
{
    public float ForceMultiplier = 2.0f;
    public void FixedUpdate()
    {
        GetComponent<Rigidbody>().AddForce(Physics.gravity * ForceMultiplier, ForceMode.Acceleration);
    }
}
