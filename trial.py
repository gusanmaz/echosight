import replicate


output = replicate.run(
  "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
  input={
    "text": "olasılığını içeren ve daha az bilinen bazı temel-bilimsel faktörler yanında, hakkında daha da zor tahminlerde bulunabildiğimiz (canlılarda \"akıl\" denen yapının evrimleşmesi, gelişmesi, bir medeniyet kurması, bilimsel ",
    "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav",
    "language": "tr",
    "cleanup_voice": True
  }
)
print(output)

exit(9)


image_path = "example.jpg"
with open(image_path, "rb") as image:
    # Run the Bakllava model for image description
    description = replicate.run(
        "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed",
        input={
            "vqa": False,
            "image": image,
            "query": "Describe this image."
        }
    )

    print("cogvlm model finished\n")
    print("English Description: " + description)

    # Run the Seamless Communication model for translation and text-to-speech
    output = replicate.run(
        "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
        input={
            "task_name": "T2TT (Text to Text translation)",
            "input_text": description,
            "input_text_language": "English",
            "target_language_text_only": "Turkish",
        }
    )
    print("Seamless Model finished\n")
    print(output)