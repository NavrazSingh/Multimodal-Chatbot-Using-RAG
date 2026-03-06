import logging
from app.services.image_service import ImageCaptioningService
from app.services.voice_service import SpeechToTextService
from app.services.vector_service import VectorDBService
from app.services.llm_service import GroqService
from app.services.pdf_loader import load_pdf_chunks

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.image_service = ImageCaptioningService()
        self.voice_service = SpeechToTextService()
        self.vector_service = VectorDBService()
        self.llm_service = GroqService()
        
        # Load sample data if index is empty
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        sample_docs = [
        """
        Complete Blood Count (CBC) Interpretation

        White Blood Cell Count (WBC)
        Normal range: 4–11 x10^9/L
        High WBC may indicate infection or inflammation.

        Hemoglobin
        Normal range:
        Men: 13.5–17.5 g/dL
        Women: 12–15 g/dL
        Low hemoglobin may indicate anemia.

        Platelet Count
        Normal range: 150–450 x10^9/L
        Low platelets may increase bleeding risk.
        """,

        """
        Blood Test Interpretation Guide

        WBC measures immune response.
        Hemoglobin measures oxygen carrying capacity.
        Platelets help blood clot.

        Doctors compare these values with normal ranges to determine if a patient is healthy.
        """
        ]

        self.vector_service.add_documents(sample_docs)

        # Load blood report dataset
        blood_chunks = load_pdf_chunks("data/blood_reports.pdf")

        # Load prescription dataset
        prescription_chunks = load_pdf_chunks("data/prescriptions.pdf")

        all_chunks = blood_chunks + prescription_chunks

        self.vector_service.add_documents(all_chunks)

        logger.info(f"Loaded {len(all_chunks)} PDF chunks into vector DB")

    def process_query(self, text_query: str = None, image_path: str = None, voice_path: str = None) -> dict:
        image_description = ""
        transcribed_text = ""
        
        # 1. Process Multimodal Inputs
        if image_path:
            image_description = self.image_service.get_caption(image_path)
            logger.info(f"Generated Image Caption: {image_description}")

        # if voice_path:
        #     transcribed_text = self.voice_service.transcribe(voice_path)
        #     logger.info(f"Transcribed Voice: {transcribed_text}")

        if voice_path:
            transcribed_text = self.voice_service.transcribe(voice_path)
            logger.info(f"Transcribed Voice: {transcribed_text}")

            # If user only sent voice, use transcription as text query
            if not text_query and transcribed_text:
                text_query = transcribed_text

        # 2. Combine inputs for retrieval
        combined_query = ""

        if text_query:
            combined_query += text_query + " "

        if transcribed_text:
            combined_query += transcribed_text + " "

        if image_description:
            combined_query += "Medical report text: " + image_description
        
        combined_query = combined_query.strip()
        if not combined_query:
            return {"answer": "I didn't receive any input to process.", "context": []}

        # 3. Retrieval
        retrieved_context = self.vector_service.search(combined_query)
        context_str = "\n".join(retrieved_context) if retrieved_context else "No relevant context found."

        # 4. Prompt Construction
        system_prompt = (
            """
            You are an AI Medical Report Analyzer.

            Your job is to help users understand medical reports and lab test results.

            Rules:
            - Explain results in simple language.
            - If a value is abnormal, explain possible reasons.
            - Provide lifestyle suggestions if relevant.
            - Always add a disclaimer that you are not a doctor.

            If the context does not contain enough information,
            say: "I couldn't find specific information in my medical database."

            Always format answers clearly with bullet points.
            """
        )
        
        if image_description.strip():

            user_prompt = f"""
        User Question:
        {text_query}

        Medical Report Text:
        {image_description}

        Medical Knowledge Context:
        {context_str}

        Analyze the medical report and return the answer in this format:

        Patient Information
        -------------------
        Patient Name:
        Test Type:

        Test Results
        ------------
        1. White Blood Cell Count
        Value:
        Normal Range:
        Status:

        2. Hemoglobin
        Value:
        Normal Range:
        Status:

        3. Platelet Count
        Value:
        Normal Range:
        Status:

        Observation
        -----------

        Lifestyle Advice
        ----------------
        """

        else:

            user_prompt = f"""
        User Question:
        {text_query}

        Relevant Medical Knowledge:
        {context_str}

        Answer the user's question clearly.

        Instructions:
        - Use bullet points
        - Keep explanation simple
        - Do not repeat the context
        - Be concise
        """

        print("OCR TEXT:", image_description)
        print("COMBINED QUERY:", combined_query)
        print("RETRIEVED CONTEXT:", retrieved_context)
        # 5. Generation
        answer = self.llm_service.generate_response(system_prompt, user_prompt)

        return {
            "answer": answer,
            "image_description": image_description,
            "transcribed_text": transcribed_text,
            "retrieved_context": retrieved_context
        }
