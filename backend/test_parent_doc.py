"""
Quick test for ParentDocumentRetrieval system
"""
import os
from app.services.retrieval_systems import ParentDocumentRetrieval

# Get API key from environment or prompt
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    print("⚠️  OPENAI_API_KEY not found in environment")
    openai_key = input("Enter your OpenAI API key: ").strip()

# Use the existing test PDF
document_path = "temp_uploads/MRL.pdf"

if not os.path.exists(document_path):
    print(f"❌ Document not found: {document_path}")
    print("Please upload a document through the UI first")
    exit(1)

print("=" * 60)
print("🧪 Testing ParentDocumentRetrieval")
print("=" * 60)

# Test config
config = {
    'parent_chunk_size': 2000,
    'parent_chunk_overlap': 200,
    'child_chunk_size': 400,
    'child_chunk_overlap': 50
}

print(f"\n📄 Document: {document_path}")
print(f"⚙️  Config: {config}")
print("\n" + "=" * 60)

# Initialize system
print("\n🔧 Initializing ParentDocumentRetrieval...")
system = ParentDocumentRetrieval(
    document_path=document_path,
    openai_api_key=openai_key,
    config=config
)

# Initialize (this loads and processes the document)
system.initialize()

print("\n" + "=" * 60)
print("✅ Initialization complete!")
print(f"   - Child chunks created: {len(system.chunks)}")
print(f"   - Initialization time: {system.initialization_time:.2f}s")
print("=" * 60)

# Test search
test_query = "What is the main topic of this document?"
print(f"\n🔍 Testing search with query: '{test_query}'")

results = system.search(test_query, k=3)

print(f"\n📊 Found {len(results)} results:")
print("=" * 60)

for i, doc in enumerate(results, 1):
    print(f"\n📄 Result {i}:")
    print(f"   Page: {doc.metadata.get('page_number', 'N/A')}")
    print(f"   Content length: {len(doc.page_content)} chars")
    print(f"   Preview: {doc.page_content[:200]}...")
    print("-" * 60)

print("\n✅ Test completed successfully!")
print("=" * 60)
