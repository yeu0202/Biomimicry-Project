using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class myRenderer : MonoBehaviour
{
    
    // Renderer rend;

    // Start is called before the first frame update
    void Start()
    {
		// rend = GetComponent<Renderer> ();
		
        // StartCoroutine(LateStart(1));

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator LateStart(float waitTime)
     {
        yield return new WaitForSeconds(waitTime);
        // Vector3 cubePosition = this.transform.position;
        // float offset1 = (float)(cubePosition[0]*0.1);
        // float offset2 = (float)(cubePosition[1]*0.1);

		// rend.material.SetTextureOffset("_MainTex", new Vector2(offset1, offset2));
        // print("texture successful");
     }
}
