# test_import.py

try:
    # Import the package and its components
    import gpt_neox_package
    from gpt_neox_package import GPTNeoXModel, GPTNeoXForCausalLM, GPTNeoXConfig

    print("Package and components imported successfully!")

    # Create instances to verify they work
    config = GPTNeoXConfig()
    model = GPTNeoXModel(config)
    causal_model = GPTNeoXForCausalLM(config)

    print("Config instance:", config)
    print("Model instance:", model)
    print("Causal Model instance:", causal_model)

except ImportError as e:
    print("Error importing package or components:", str(e))
except Exception as e:
    print("An error occurred:", str(e))
