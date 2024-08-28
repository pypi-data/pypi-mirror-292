from opensesame import OpenSesame_openai
from opensesame import OpenSesame_gemini
from opensesame import OpenSesame_anthropic 
from opensesame import OpenSesame_groq
# openai test
def test_openai() :
    client = OpenSesame_openai({
        'api_key': 'sk-proj-PneFGMEv3i6fIG7SBWNeT3BlbkFJtqK96SxiUvvVy33Syefx',
        'open_sesame_key': '6def3c47-847e-428d-a7bd-899da351a19c',
        'project_name': 'abadabadab',  # Make sure this is correct
        'ground_truth': 'hi',
        'context': 'hello'
    })

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "What is the capital of thailand!"}]
        )
        print("*********")
        print(completion)
    except Exception as e:
        print(f"An error occurred: {e}")

# gemini test
def test_gemini() :
    client = OpenSesame_gemini({
        "api_key" : "AIzaSyAeCyuUxv7n6ngMwRZdQCDNOt-Tu9-DIpo",
        "open_sesame_key" : '6def3c47-847e-428d-a7bd-899da351a19c',
        'project_name': 'abadabadab',  # Make sure this is correct
        'ground_truth': 'hi',
        'context': 'hello'
    })

    try :
        response = client.GenerativeModel(model_name="gemini-1.5-pro").generate_content(prompt="What is the capital of thailand")
        print(response)
    except Exception as e:
        print(f"An error occured {e}")

def test_anthropic() :

    client = OpenSesame_anthropic({
    'api_key': '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',
    'open_sesame_key': '6def3c47-847e-428d-a7bd-899da351a19c',
    'project_name': 'abadabadab',
    'ground_truth': 'idk',
    'context': 'Hi'
    })

    message = client.Messages(client).create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, What is a pulsar"}
        ]
    )
    print(message)

def test_groq() :
    client = OpenSesame_groq({
    'api_key': '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',
    'open_sesame_key': '6def3c47-847e-428d-a7bd-899da351a19c',
    'project_name': 'groq_test',
    'ground_truth': 'No idea',
    'context': 'Math'
    })
    
    result = client.ChatCompletions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": "What is 1606 * 1708 ?"}
        ]
    )

    print(result)

test_groq()




