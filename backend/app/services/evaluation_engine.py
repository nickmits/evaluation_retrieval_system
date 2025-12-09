"""
Evaluation Engine
Handles RAGAS evaluation pipeline for retrieval systems
"""

from typing import Dict, Any, List, Optional
import sys
import asyncio
import nest_asyncio
from ragas import EvaluationDataset, evaluate, RunConfig
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import (
    LLMContextRecall,
    Faithfulness,
    FactualCorrectness,
    AnswerRelevancy,
    ContextPrecision
)
from ragas.testset import TestsetGenerator
from ragas.testset.synthesizers import (
    SingleHopSpecificQuerySynthesizer,
    MultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .retrieval_systems import RetrievalSystemFactory, BaseRetrievalSystem

# Apply nest_asyncio for nested event loops
nest_asyncio.apply()

# Fix for Windows event loop issues
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class EvaluationEngine:
    """Engine for running RAGAS evaluations on retrieval systems"""

    def __init__(
        self,
        document_path: str,
        openai_api_key: str,
        cohere_api_key: Optional[str] = None
    ):
        self.document_path = document_path
        self.openai_api_key = openai_api_key
        self.cohere_api_key = cohere_api_key

        # Initialize evaluator models
        self.evaluator_llm = LangchainLLMWrapper(
            ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
        )
        self.evaluator_embeddings = LangchainEmbeddingsWrapper(
            OpenAIEmbeddings(api_key=openai_api_key)
        )

    def generate_test_dataset(
        self,
        num_questions: int = 10,
        use_multihop: bool = False
    ) -> EvaluationDataset:
        """Generate test questions from the document"""

        print(f"[TESTSET] Generating {num_questions} test questions...")

        # Load and chunk document for test generation
        loader = PyMuPDFLoader(self.document_path)
        pages = loader.load()

        # Use RecursiveCharacterTextSplitter for test generation
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(pages)

        print(f"[TESTSET] Using {len(chunks)} chunks for question generation")

        # Initialize test generator
        generator_llm = LangchainLLMWrapper(
            ChatOpenAI(model="gpt-4o-mini", api_key=self.openai_api_key)
        )
        generator_embeddings = LangchainEmbeddingsWrapper(
            OpenAIEmbeddings(api_key=self.openai_api_key)
        )

        generator = TestsetGenerator(
            llm=generator_llm,
            embedding_model=generator_embeddings
        )

        # Define query distribution - Always use simple for now to avoid RAGAS bugs
        # Multi-hop has compatibility issues with newer RAGAS versions
        query_distribution = [
            (SingleHopSpecificQuerySynthesizer(llm=generator_llm), 1.0)
        ]

        if use_multihop:
            print("[TESTSET] Note: Multi-hop questions disabled due to RAGAS compatibility issues")
            print("[TESTSET] Using single-hop questions only for better stability")

        # Generate test dataset with error handling
        chunks_to_use = min(20, len(chunks))

        try:
            test_dataset = generator.generate_with_langchain_docs(
                chunks[:chunks_to_use],
                testset_size=num_questions,
                query_distribution=query_distribution
            )
            print(f"[TESTSET] Generated {len(test_dataset)} questions")
        except Exception as e:
            print(f"[TESTSET] Warning: RAGAS generation failed: {e}")
            print("[TESTSET] Falling back to manual question generation...")
            # Fallback: Create simple dataset manually
            test_dataset = self._generate_simple_test_dataset(chunks[:chunks_to_use], num_questions)

        return test_dataset

    def _generate_simple_test_dataset(self, chunks: List, num_questions: int) -> EvaluationDataset:
        """Fallback method to generate simple test questions"""
        import pandas as pd
        from langchain_openai import ChatOpenAI

        print(f"[TESTSET] Creating {num_questions} questions manually...")

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=self.openai_api_key, temperature=0.7)

        # Select diverse chunks
        step = max(1, len(chunks) // num_questions)
        selected_chunks = chunks[::step][:num_questions]

        questions = []
        for i, chunk in enumerate(selected_chunks):
            prompt = f"""Based on this text, generate a specific factual question that can be answered from this content:

Text: {chunk.page_content[:500]}

Generate ONE clear, specific question:"""

            try:
                response = llm.invoke(prompt)
                question = response.content.strip()

                # Create ground truth answer
                answer_prompt = f"""Answer this question based on the text:

Text: {chunk.page_content}

Question: {question}

Answer:"""
                answer_response = llm.invoke(answer_prompt)
                answer = answer_response.content.strip()

                questions.append({
                    "user_input": question,
                    "reference": answer,
                    "reference_contexts": [chunk.page_content]
                })

                print(f"  Generated question {i+1}/{num_questions}")
            except Exception as e:
                print(f"  Failed to generate question {i+1}: {e}")

        # Create DataFrame and convert to EvaluationDataset
        df = pd.DataFrame(questions)
        return EvaluationDataset.from_pandas(df)

    def evaluate_system(
        self,
        system_type: str,
        system_config: Dict[str, Any],
        num_test_questions: int = 10,
        use_multihop: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a single retrieval system

        Args:
            system_type: Type of retrieval system
            system_config: Configuration for the system
            num_test_questions: Number of test questions to generate
            use_multihop: Whether to include multi-hop questions

        Returns:
            Dictionary containing evaluation results and metrics
        """

        print(f"\n{'='*70}")
        print(f"EVALUATING: {system_type}")
        print(f"{'='*70}")

        # Step 1: Generate test dataset
        test_dataset = self.generate_test_dataset(num_test_questions, use_multihop)

        # Step 2: Initialize retrieval system
        print(f"\n[SYSTEM] Initializing {system_type}...")
        retrieval_system = RetrievalSystemFactory.create_system(
            system_type=system_type,
            document_path=self.document_path,
            openai_api_key=self.openai_api_key,
            cohere_api_key=self.cohere_api_key,
            config=system_config
        )
        retrieval_system.initialize()

        # Step 3: Create evaluation chain
        chain = RetrievalChain(retrieval_system, self.openai_api_key)

        # Step 4: Process questions
        df_questions = test_dataset.to_pandas()
        dataset = EvaluationDataset.from_pandas(df_questions)
        self._reset_eval_fields(dataset)

        print(f"\n[EVALUATION] Processing {len(dataset)} questions...")

        for i, row in enumerate(dataset):
            q = getattr(row, "user_input", None) or getattr(row, "question", None)
            if not q:
                continue

            print(f"  [{i+1}/{len(dataset)}] {q[:60]}...")

            # Invoke chain
            out = chain.invoke({"question": q})

            # Store results
            row.response = self._to_text(out["response"])
            row.retrieved_contexts = [d.page_content for d in out["context"]][:10]

        # Step 5: Run RAGAS evaluation
        print(f"\n[RAGAS] Running metrics evaluation...")
        ragas_results = self._run_ragas_evaluation(dataset)

        # Step 6: Compile results
        results = self._compile_results(
            ragas_results=ragas_results,
            system_info=retrieval_system.get_metrics_summary(),
            test_dataset=df_questions
        )

        print(f"\n{'='*70}")
        print(f"EVALUATION COMPLETE: {system_type}")
        print(f"{'='*70}\n")

        return results

    def _run_ragas_evaluation(self, dataset: EvaluationDataset) -> Any:
        """Run RAGAS evaluation with all metrics"""

        metrics = [
            LLMContextRecall(),
            Faithfulness(),
            ContextPrecision(),
            AnswerRelevancy(),
            FactualCorrectness()
        ]

        results = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=self.evaluator_llm,
            embeddings=self.evaluator_embeddings,
            run_config=RunConfig(timeout=360),
            raise_exceptions=False
        )

        return results

    def _compile_results(
        self,
        ragas_results: Any,
        system_info: Dict[str, Any],
        test_dataset: Any
    ) -> Dict[str, Any]:
        """Compile evaluation results into a structured format"""

        # Convert RAGAS results to DataFrame
        if hasattr(ragas_results, 'to_pandas'):
            df_results = ragas_results.to_pandas()
        else:
            df_results = ragas_results

        # Debug: Print available columns
        print(f"\n[DEBUG] RAGAS results columns: {list(df_results.columns)}")
        print(f"[DEBUG] DataFrame shape: {df_results.shape}")
        print(f"[DEBUG] First few rows:\n{df_results.head()}")

        # Extract metrics
        metrics = {
            'faithfulness': 0.0,
            'context_recall': 0.0,
            'context_precision': 0.0,
            'answer_relevancy': 0.0,
            'factual_correctness': 0.0
        }

        metric_columns = [
            'faithfulness',
            'context_recall',
            'context_precision',
            'answer_relevancy',
            'factual_correctness(mode=f1)'
        ]

        for col in metric_columns:
            if col in df_results.columns:
                key = col.replace('(mode=f1)', '')
                metrics[key] = float(df_results[col].mean())
                print(f"[DEBUG] Found metric '{key}': {metrics[key]}")

        # Calculate average score
        avg_score = sum(metrics.values()) / len(metrics)

        return {
            "system_info": system_info,
            "metrics": metrics,
            "average_score": avg_score,
            "num_test_questions": len(test_dataset),
            "detailed_results": df_results.to_dict('records') if hasattr(df_results, 'to_dict') else []
        }

    @staticmethod
    def _reset_eval_fields(dataset):
        """Reset evaluation fields in dataset"""
        for row in dataset:
            if hasattr(row, 'eval_sample'):
                row.eval_sample.response = None
                row.eval_sample.retrieved_contexts = []
            else:
                row.response = None
                row.retrieved_contexts = []

    @staticmethod
    def _to_text(content):
        """Helper to convert content to text"""
        if isinstance(content, str):
            return content
        return str(content)


class RetrievalChain:
    """Wrapper chain for retrieval system evaluation"""

    def __init__(self, retrieval_system: BaseRetrievalSystem, openai_api_key: str):
        self.retrieval_system = retrieval_system
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retrieval and answer generation"""

        question = inputs.get("question", "")

        try:
            # Retrieve relevant contexts
            raw_contexts = self.retrieval_system.search(question, k=10)

            # Generate answer
            context_text = "\n\n".join([
                f"[Context {i+1}]: {doc.page_content}"
                for i, doc in enumerate(raw_contexts[:5])
            ])

            prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {question}

Answer (be specific and use information from the context):"""

            response = self.llm.invoke(prompt)

            return {
                "response": response.content,
                "context": raw_contexts[:10]
            }

        except Exception as e:
            print(f"    Error in retrieval: {e}")
            return {
                "response": f"Error: {str(e)}",
                "context": []
            }
