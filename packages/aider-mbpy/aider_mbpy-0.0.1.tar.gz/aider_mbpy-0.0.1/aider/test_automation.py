import os
import unittest
from unittest.mock import MagicMock, patch

import requests
import json
import concurrent.futures

class TestAutomation:
    def __init__(self, coder, max_iterations: int = 10):
        self.coder = coder
        self.max_iterations = max_iterations

    def run_automated_testing(self, instructions):
        self.coder.io.tool_output("Step 1: Analyzing instructions and generating implementation")
        implementation = self.coder.run(f"Analyze the following instructions and generate or modify the implementation accordingly:\n{instructions}")
        
        self.coder.io.tool_output("Step 2: Generating test cases")
        test_cases = self.coder.run("Generate comprehensive test cases for the implementation. Include both normal cases and edge cases.")
        
        chain_of_thought_log = []
        
        for attempt in range(1, self.max_iterations + 1):
            self.coder.io.tool_output(f"Attempt {attempt} of {self.max_iterations}")
            result = self.automate_testing(instructions, implementation, test_cases)
            
            chain_of_thought = f"Attempt {attempt}: "
            
            if result:
                chain_of_thought += f"Success! All tests passed on attempt {attempt}"
                self.coder.io.tool_output(chain_of_thought)
                chain_of_thought_log.append(chain_of_thought)
                break
            else:
                chain_of_thought += self.analyze_failure(instructions, implementation, test_cases)
                chain_of_thought_log.append(chain_of_thought)
                
                self.coder.io.tool_output("Modifying the implementation and tests based on analysis")
                implementation, test_cases = self.modify_implementation_and_tests(instructions, implementation, test_cases, chain_of_thought)
        
        # Save the chain of thought log
        log_file = f"test_automation_log_{instructions[:50]}.txt"  # Use first 50 chars of instructions for filename
        with open(log_file, "w") as f:
            f.write("\n\n".join(chain_of_thought_log))
        
        self.coder.io.tool_output(f"Chain of thought log saved to {log_file}")
        
        return result, log_file

    def automate_testing(self, instructions, implementation, test_cases):
        self.coder.io.tool_output("Running tests...")
        test_result = self.run_test(implementation, test_cases)
        return test_result

    def run_test(self, implementation, test_cases):
        try:
            exec(implementation)
            exec(test_cases)
            return True
        except Exception as e:
            self.coder.io.tool_error(f"Test failed: {str(e)}")
            return False

    def analyze_failure(self, instructions, implementation, test_cases):
        self.coder.io.tool_output("Analyzing test failure...")
        analysis = self.coder.run(f"Analyze the following implementation and test cases. Identify potential issues and suggest improvements:\n\nImplementation:\n{implementation}\n\nTest Cases:\n{test_cases}")
        return analysis

    def modify_implementation_and_tests(self, instructions, implementation, test_cases, analysis):
        self.coder.io.tool_output("Modifying implementation and tests...")
        modification = self.coder.run(f"Based on the following analysis, modify the implementation and test cases:\n\nAnalysis:\n{analysis}\n\nCurrent Implementation:\n{implementation}\n\nCurrent Test Cases:\n{test_cases}")
        
        # Extract modified implementation and test cases from the modification
        new_implementation = self.extract_code(modification, "Implementation")
        new_test_cases = self.extract_code(modification, "Test Cases")
        
        return new_implementation, new_test_cases

    def extract_code(self, text, section):
        start = text.find(f"{section}:")
        if start == -1:
            return ""
        start = text.find("```", start)
        if start == -1:
            return ""
        start += 3
        end = text.find("```", start)
        if end == -1:
            return text[start:]
        return text[start:end].strip()

    def test_vllm_server(self):
        # Use the persistent server for testing
        base_url = "http://localhost:8000"

        try:
            # Make a simple request to check if the server is running
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("vLLM server is running!")
                return True
            else:
                print(f"vLLM server returned unexpected status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to the vLLM server: {e}")
            return False

    def query_llama(self, prompt):
        base_url = "http://localhost:8000"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "max_tokens": 100
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["generated_text"]

    def run_vllm_server_tests(self, base_url, headers):
        # Test 1: Basic text generation
        data = {
            "prompt": "Once upon a time",
            "max_tokens": 50
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        assert "generated_text" in result, "Response does not contain 'generated_text'"
        assert len(result["generated_text"]) > 0, "Generated text is empty"
        print("Test 1: Basic text generation passed")

        # Test 2: Generation with different parameters
        data = {
            "prompt": "The future of AI is",
            "max_tokens": 100,
            "temperature": 0.9,
            "top_p": 0.8,
            "top_k": 40
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        assert "generated_text" in result, "Response does not contain 'generated_text'"
        assert len(result["generated_text"]) > 0, "Generated text is empty"
        print("Test 2: Generation with different parameters passed")

        # Test 3: Error handling (invalid parameters)
        data = {
            "prompt": "Test prompt",
            "max_tokens": -1
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        assert response.status_code == 422, "Server should return 422 for invalid parameters"
        print("Test 3: Error handling (invalid parameters) passed")

        # Test 4: Long prompt handling
        long_prompt = "a" * 4096
        data = {
            "prompt": long_prompt,
            "max_tokens": 50
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        assert response.status_code == 200, f"Long prompt handling failed with status code {response.status_code}"
        print("Test 4: Long prompt handling passed")

        # Test 5: Concurrent requests
        def make_request():
            data = {
                "prompt": "Concurrent test",
                "max_tokens": 20
            }
            response = requests.post(f"{base_url}/generate", json=data, headers=headers)
            return response.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, range(5)))
        
        assert all(status == 200 for status in results), "Concurrent requests test failed"
        print("Test 5: Concurrent requests passed")

        # Test 6: Consistency in output
        data = {
            "prompt": "The capital of France is",
            "max_tokens": 10,
            "temperature": 0.0
        }
        responses = [requests.post(f"{base_url}/generate", json=data, headers=headers).json() for _ in range(3)]
        assert all(r["generated_text"] == responses[0]["generated_text"] for r in responses), "Inconsistent output with temperature 0"
        print("Test 6: Consistency in output passed")

        # Test 7: Different output with high temperature
        data["temperature"] = 1.0
        responses = [requests.post(f"{base_url}/generate", json=data, headers=headers).json() for _ in range(3)]
        assert any(r["generated_text"] != responses[0]["generated_text"] for r in responses), "Output doesn't vary with high temperature"
        print("Test 7: Different output with high temperature passed")

        # Test 8: Prompt continuation
        data = {
            "prompt": "The quick brown fox",
            "max_tokens": 20
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        result = response.json()
        assert data["prompt"] in result["generated_text"], "Generated text doesn't continue the prompt"
        print("Test 8: Prompt continuation passed")

        # Test 9: Multi-turn conversation
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": "What's its population?"}
        ]
        data = {
            "prompt": json.dumps(conversation),
            "max_tokens": 50
        }
        response = requests.post(f"{base_url}/generate", json=data, headers=headers)
        result = response.json()
        assert "million" in result["generated_text"].lower(), "Multi-turn conversation failed"
        print("Test 9: Multi-turn conversation passed")

        return True

    def run_vllm_tests(self):
        print("Running vLLM server tests...")
        result = self.test_vllm_server()
        if result:
            print("All vLLM server tests passed successfully!")
        else:
            print("vLLM server tests failed.")
        return result

class TestAutomationTests(unittest.TestCase):
    def setUp(self):
        self.mock_coder = MagicMock()
        self.test_automation = TestAutomation(self.mock_coder)

    def test_run_automated_testing(self):
        self.mock_coder.run.side_effect = [
            "mock implementation",
            "mock test cases",
            "mock analysis",
            "mock modification"
        ]
        self.test_automation.automate_testing = MagicMock(side_effect=[False, True])
        self.test_automation.extract_code = MagicMock(side_effect=["new implementation", "new test cases"])

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            result, log_file = self.test_automation.run_automated_testing("test instructions")

        self.assertTrue(result)
        self.assertEqual(log_file, "test_automation_log_test instructions.txt")
        self.assertEqual(self.mock_coder.run.call_count, 4)
        self.assertEqual(self.test_automation.automate_testing.call_count, 2)
        mock_file.assert_called_once_with("test_automation_log_test instructions.txt", "w")

    def test_aider_automated_testing(self):
        # Create a real TestAutomation instance
        from aider.coders import Coder
        from aider.io import InputOutput
        from aider.models import Model

        io = InputOutput()
        model = Model("gpt-3.5-turbo")
        coder = Coder.create(main_model=model, io=io)
        test_automation = TestAutomation(coder)

        # Function to run automated testing with new history files
        def run_with_new_history_files():
            # Generate unique file names
            import uuid
            unique_id = uuid.uuid4().hex
            chat_history_file = f"chat_history_{unique_id}.jsonl"
            llm_history_file = f"llm_history_{unique_id}.jsonl"
            input_history_file = f"input_history_{unique_id}.txt"

            # Set new history files
            coder.io.chat_history_file = chat_history_file
            coder.llm_history_file = llm_history_file
            coder.io.input_history_file = input_history_file

            # Run the automated testing
            result, log_file = test_automation.run_automated_testing("Implement a simple calculator function")

            # Clean up the new history files
            for file in [chat_history_file, llm_history_file, input_history_file]:
                if os.path.exists(file):
                    os.remove(file)

            return result, log_file

        # Run the test with new history files
        result, log_file = run_with_new_history_files()

        # Assert that the result is successful
        self.assertTrue(result)

        # Check if the log file was created
        self.assertTrue(os.path.exists(log_file))

        # Read the log file and check its contents
        with open(log_file, 'r') as f:
            log_content = f.read()

        # Assert that the log contains expected information
        self.assertIn("Attempt 1:", log_content)
        self.assertIn("Success!", log_content)

        # Clean up the log file
        os.remove(log_file)

    def test_automate_testing(self):
        self.test_automation.run_test = MagicMock(return_value=True)
        result = self.test_automation.automate_testing("instructions", "implementation", "test_cases")
        self.assertTrue(result)
        self.test_automation.run_test.assert_called_once_with("implementation", "test_cases")

    def test_run_test_success(self):
        with patch('builtins.exec') as mock_exec:
            result = self.test_automation.run_test("def test(): pass", "test()")
        self.assertTrue(result)
        self.assertEqual(mock_exec.call_count, 2)

    def test_run_test_failure(self):
        with patch('builtins.exec') as mock_exec:
            mock_exec.side_effect = [None, AssertionError("Test failed")]
            result = self.test_automation.run_test("def test(): assert False", "test()")
        self.assertFalse(result)
        self.assertEqual(mock_exec.call_count, 2)

    def test_analyze_failure(self):
        self.mock_coder.run.return_value = "mock analysis"
        result = self.test_automation.analyze_failure("instructions", "implementation", "test_cases")
        self.assertEqual(result, "mock analysis")
        self.mock_coder.run.assert_called_once()

    def test_modify_implementation_and_tests(self):
        self.mock_coder.run.return_value = "mock modification"
        self.test_automation.extract_code = MagicMock(side_effect=["new implementation", "new test cases"])
        new_impl, new_tests = self.test_automation.modify_implementation_and_tests("instructions", "implementation", "test_cases", "analysis")
        self.assertEqual(new_impl, "new implementation")
        self.assertEqual(new_tests, "new test cases")
        self.mock_coder.run.assert_called_once()
        self.assertEqual(self.test_automation.extract_code.call_count, 2)

    def test_extract_code(self):
        text = "Implementation:\n```\ndef test(): pass\n```\nTest Cases:\n```\ntest()\n```"
        result = self.test_automation.extract_code(text, "Implementation")
        self.assertEqual(result, "def test(): pass")
        result = self.test_automation.extract_code(text, "Test Cases")
        self.assertEqual(result, "test()")

    def test_run_vllm_tests(self):
        # Mock the test_vllm_server method to avoid actually starting a server
        with patch.object(TestAutomation, 'test_vllm_server', return_value=True):
            result = self.test_automation.run_vllm_tests()
            self.assertTrue(result)
            self.test_automation.test_vllm_server.assert_called_once()

if __name__ == "__main__":
    unittest.main(verbosity=2)

    # Add a simple way to test the vLLM server
    test_automation = TestAutomation(None)  # We don't need a coder instance for this test
    server_running = test_automation.test_vllm_server()
    print(f"vLLM server is {'running' if server_running else 'not running'}")
