import json
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from recommendations.policy_tracking.models import PolicyRecommendation

User = get_user_model()


class AIConversation(models.Model):
    """Model for storing AI assistant conversations."""

    CONVERSATION_TYPES = [
        ("policy_chat", "Policy Chat"),
        ("document_generation", "Document Generation"),
        ("analysis", "Policy Analysis"),
        ("evidence_review", "Evidence Review"),
        ("cultural_guidance", "Cultural Guidance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
        help_text="User who initiated the conversation",
    )

    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default="policy_chat",
        help_text="Type of AI conversation",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Conversation title (auto-generated or user-defined)",
    )

    # Related objects
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_conversations",
        help_text="Policy recommendation this conversation relates to",
    )

    # Conversation metadata
    messages = models.JSONField(
        default=list, help_text="Array of conversation messages with roles and content"
    )

    context_data = models.JSONField(
        default=dict, help_text="Additional context data for the conversation"
    )

    # AI model settings
    model_used = models.CharField(
        max_length=50,
        default="gemini-2.5-flash",
        help_text="AI model used for this conversation",
    )

    # Status and metadata
    is_active = models.BooleanField(
        default=True, help_text="Whether this conversation is active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "conversation_type"]),
            models.Index(fields=["related_policy", "is_active"]),
            models.Index(fields=["created_at", "user"]),
        ]

    def __str__(self):
        date_str = self.created_at.strftime("%Y-%m-%d")
        return self.title or f"{self.conversation_type} - {date_str}"

    def add_message(self, role, content, metadata=None):
        """Add a message to the conversation."""
        message = {
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": timezone.now().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)
        self.save(update_fields=["messages", "updated_at"])

    @property
    def message_count(self):
        """Get the number of messages in this conversation."""
        return len(self.messages)

    @property
    def last_message_time(self):
        """Get the timestamp of the last message."""
        if self.messages:
            return self.messages[-1].get("timestamp")
        return None


class AIInsight(models.Model):
    """Model for storing AI-generated insights about policies and communities."""

    INSIGHT_TYPES = [
        ("policy_analysis", "Policy Analysis"),
        ("impact_prediction", "Impact Prediction"),
        ("stakeholder_analysis", "Stakeholder Analysis"),
        ("cultural_considerations", "Cultural Considerations"),
        ("implementation_guidance", "Implementation Guidance"),
        ("evidence_synthesis", "Evidence Synthesis"),
        ("risk_assessment", "Risk Assessment"),
        ("opportunity_identification", "Opportunity Identification"),
    ]

    CONFIDENCE_LEVELS = [
        ("high", "High Confidence"),
        ("medium", "Medium Confidence"),
        ("low", "Low Confidence"),
        ("experimental", "Experimental"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, help_text="Title of the insight")

    insight_type = models.CharField(
        max_length=30, choices=INSIGHT_TYPES, help_text="Type of insight generated"
    )

    content = models.TextField(help_text="Detailed content of the AI insight")

    summary = models.TextField(blank=True, help_text="Brief summary of the insight")

    # Relationships
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name="ai_insights",
        help_text="Policy recommendation this insight relates to",
    )

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insights",
        help_text="Conversation that generated this insight",
    )

    # AI metadata
    model_used = models.CharField(
        max_length=50,
        default="gemini-2.5-flash",
        help_text="AI model used to generate this insight",
    )

    confidence_level = models.CharField(
        max_length=15,
        choices=CONFIDENCE_LEVELS,
        default="medium",
        help_text="Confidence level of the AI insight",
    )

    # Structured data
    key_points = models.JSONField(
        default=list, help_text="Key points extracted from the insight"
    )

    recommendations = models.JSONField(
        default=list, help_text="Specific recommendations from the insight"
    )

    cultural_considerations = models.JSONField(
        default=list, help_text="Cultural considerations for Bangsamoro communities"
    )

    # Validation and review
    is_validated = models.BooleanField(
        default=False,
        help_text="Whether this insight has been validated by human experts",
    )

    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_insights",
        help_text="User who validated this insight",
    )

    validation_notes = models.TextField(
        blank=True, help_text="Notes from human validation"
    )

    # Usage tracking
    view_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this insight has been viewed"
    )

    usefulness_score = models.FloatField(
        null=True, blank=True, help_text="User-rated usefulness score (0-5)"
    )

    # Metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="generated_insights",
        help_text="User who generated this insight",
    )

    tags = models.JSONField(
        default=list, help_text="Tags for categorizing and searching insights"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["related_policy", "insight_type"]),
            models.Index(fields=["is_validated", "confidence_level"]),
            models.Index(fields=["created_at", "insight_type"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.insight_type}"

    def increment_view_count(self):
        """Increment the view count for this insight."""
        self.view_count += 1
        self.save(update_fields=["view_count"])


class AIGeneratedDocument(models.Model):
    """Model for storing AI-generated documents like policy briefs and reports."""

    DOCUMENT_TYPES = [
        ("policy_brief", "Policy Brief"),
        ("executive_summary", "Executive Summary"),
        ("implementation_plan", "Implementation Plan"),
        ("impact_assessment", "Impact Assessment"),
        ("stakeholder_report", "Stakeholder Report"),
        ("cultural_analysis", "Cultural Analysis"),
        ("evidence_report", "Evidence Report"),
        ("recommendation_memo", "Recommendation Memo"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=255, help_text="Title of the generated document"
    )

    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, help_text="Type of document generated"
    )

    content = models.TextField(help_text="Generated document content")

    # Relationships
    related_policy = models.ForeignKey(
        PolicyRecommendation,
        on_delete=models.CASCADE,
        related_name="ai_generated_documents",
        help_text="Policy recommendation this document relates to",
    )

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_documents",
        help_text="Conversation that generated this document",
    )

    # Generation metadata
    prompt_used = models.TextField(help_text="Prompt used to generate this document")

    model_used = models.CharField(
        max_length=50,
        default="gemini-2.5-flash",
        help_text="AI model used to generate this document",
    )

    generation_parameters = models.JSONField(
        default=dict, help_text="Parameters used for document generation"
    )

    # Document structure
    sections = models.JSONField(
        default=list, help_text="Document sections with titles and content"
    )

    key_points = models.JSONField(
        default=list, help_text="Key points extracted from the document"
    )

    # Review and approval
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Document status",
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_ai_documents",
        help_text="User who reviewed this document",
    )

    review_notes = models.TextField(
        blank=True, help_text="Review comments and feedback"
    )

    # Export formats
    pdf_file = models.FileField(
        upload_to="ai_documents/pdf/%Y/%m/",
        null=True,
        blank=True,
        help_text="Generated PDF version",
    )

    word_file = models.FileField(
        upload_to="ai_documents/word/%Y/%m/",
        null=True,
        blank=True,
        help_text="Generated Word document version",
    )

    # Metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="generated_documents",
        help_text="User who generated this document",
    )

    download_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this document has been downloaded"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["related_policy", "document_type"]),
            models.Index(fields=["status", "document_type"]),
            models.Index(fields=["created_at", "generated_by"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.document_type}"

    def increment_download_count(self):
        """Increment the download count for this document."""
        self.download_count += 1
        self.save(update_fields=["download_count"])


class AIUsageMetrics(models.Model):
    """Model for tracking AI usage metrics and analytics."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ai_usage_metrics"
    )

    date = models.DateField(default=timezone.now)

    # Usage counts
    conversations_started = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    insights_generated = models.PositiveIntegerField(default=0)
    documents_created = models.PositiveIntegerField(default=0)

    # Feature usage
    policy_analysis_used = models.PositiveIntegerField(default=0)
    document_generation_used = models.PositiveIntegerField(default=0)
    cultural_guidance_used = models.PositiveIntegerField(default=0)
    evidence_review_used = models.PositiveIntegerField(default=0)

    # Performance metrics
    average_response_time = models.FloatField(null=True, blank=True)
    total_tokens_used = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date", "user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"AI Usage - {self.user.username} - {self.date}"


class DocumentEmbedding(models.Model):
    """
    Model for tracking which documents have been indexed in the vector store.

    This model stores metadata about embeddings without storing the actual
    embedding vectors (those are stored in FAISS indices for performance).
    """

    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of object that was embedded"
    )
    object_id = models.PositiveIntegerField(help_text="ID of the embedded object")
    content_object = GenericForeignKey('content_type', 'object_id')

    # Embedding metadata
    embedding_hash = models.CharField(
        max_length=64,
        help_text="MD5 hash of content (used to detect changes)"
    )

    model_used = models.CharField(
        max_length=100,
        default='sentence-transformers/all-MiniLM-L6-v2',
        help_text="Embedding model used"
    )

    dimension = models.PositiveIntegerField(
        default=384,
        help_text="Embedding vector dimension"
    )

    # Index information
    index_name = models.CharField(
        max_length=50,
        help_text="Name of the vector store index (e.g., 'communities', 'assessments')"
    )

    index_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Position in the FAISS index"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['content_type', 'object_id', 'index_name']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['index_name', 'updated_at']),
            models.Index(fields=['embedding_hash']),
        ]

    def __str__(self):
        return f"Embedding: {self.content_type.model} #{self.object_id} in {self.index_name}"

    @property
    def needs_update(self) -> bool:
        """
        Check if the embedding needs to be updated.

        This would require accessing the actual object and computing its hash,
        so it's implemented in the service layer.
        """
        return False  # Placeholder

    @classmethod
    def is_indexed(cls, obj, index_name: str) -> bool:
        """
        Check if an object is already indexed.

        Args:
            obj: Django model instance
            index_name: Name of the index

        Returns:
            True if object is indexed
        """
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            index_name=index_name
        ).exists()

    @classmethod
    def get_or_create_for_object(cls, obj, index_name: str, embedding_hash: str):
        """
        Get or create a DocumentEmbedding for an object.

        Args:
            obj: Django model instance
            index_name: Name of the index
            embedding_hash: MD5 hash of content

        Returns:
            Tuple of (DocumentEmbedding, created)
        """
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.get_or_create(
            content_type=content_type,
            object_id=obj.id,
            index_name=index_name,
            defaults={
                'embedding_hash': embedding_hash,
            }
        )


class AIOperation(models.Model):
    """
    Model for logging AI operations and tracking costs.

    This model tracks every AI API call for:
    - Cost monitoring and budgeting
    - Performance analysis
    - Error tracking
    - Usage analytics
    """

    OPERATION_TYPES = [
        ('chat', 'Chat/Conversation'),
        ('analysis', 'Policy Analysis'),
        ('document_generation', 'Document Generation'),
        ('evidence_review', 'Evidence Review'),
        ('cultural_guidance', 'Cultural Guidance'),
        ('needs_classification', 'Needs Classification'),
        ('other', 'Other'),
    ]

    MODULE_CHOICES = [
        ('general', 'General'),
        ('mana', 'Mapping & Needs Assessment'),
        ('coordination', 'Coordination'),
        ('communities', 'Communities'),
        ('policies', 'Policy Tracking'),
        ('project_central', 'Project Central'),
    ]

    # Basic info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_TYPES,
        help_text="Type of AI operation"
    )
    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        default='general',
        help_text="OBCMS module where operation was performed"
    )

    # User info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_operations',
        help_text="User who initiated the operation"
    )

    # Technical details
    prompt_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA256 hash of prompt (for cache key tracking)"
    )
    model_used = models.CharField(
        max_length=50,
        default='gemini-1.5-pro',
        help_text="AI model used for this operation"
    )

    # Performance metrics
    tokens_used = models.IntegerField(
        default=0,
        help_text="Total tokens used (input + output)"
    )
    response_time = models.FloatField(
        help_text="Response time in seconds"
    )

    # Cost tracking
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Cost of operation in USD"
    )

    # Status
    success = models.BooleanField(
        default=True,
        help_text="Whether operation succeeded"
    )
    error = models.TextField(
        blank=True,
        help_text="Error message if operation failed"
    )
    error_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Error category (rate_limit, timeout, etc.)"
    )

    # Caching
    cached = models.BooleanField(
        default=False,
        help_text="Whether response was served from cache"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['operation_type', 'created_at']),
            models.Index(fields=['module', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['cached', 'created_at']),
        ]

    def __str__(self):
        status = "✓" if self.success else "✗"
        cache_status = "(cached)" if self.cached else ""
        return (
            f"{status} {self.operation_type} | "
            f"{self.module} | "
            f"${self.cost:.4f} | "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')} "
            f"{cache_status}"
        )

    @classmethod
    def log_operation(
        cls,
        operation_type: str,
        module: str,
        prompt_hash: str,
        model_used: str,
        tokens_used: int,
        cost: float,
        response_time: float,
        success: bool,
        user=None,
        error: str = '',
        error_category: str = '',
        cached: bool = False
    ):
        """
        Log an AI operation.

        Args:
            operation_type: Type of operation
            module: OBCMS module
            prompt_hash: Hash of prompt
            model_used: AI model
            tokens_used: Token count
            cost: Operation cost
            response_time: Response time in seconds
            success: Success status
            user: User object (optional)
            error: Error message (optional)
            error_category: Error category (optional)
            cached: Whether cached (optional)

        Returns:
            AIOperation instance
        """
        return cls.objects.create(
            operation_type=operation_type,
            module=module,
            prompt_hash=prompt_hash,
            model_used=model_used,
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            success=success,
            user=user,
            error=error,
            error_category=error_category,
            cached=cached
        )

    @classmethod
    def get_daily_stats(cls, date=None):
        """Get statistics for a specific day."""
        if date is None:
            date = timezone.now().date()

        operations = cls.objects.filter(
            created_at__date=date
        )

        return {
            'total_operations': operations.count(),
            'successful': operations.filter(success=True).count(),
            'failed': operations.filter(success=False).count(),
            'cached': operations.filter(cached=True).count(),
            'total_cost': operations.aggregate(
                total=models.Sum('cost')
            )['total'] or 0,
            'total_tokens': operations.aggregate(
                total=models.Sum('tokens_used')
            )['total'] or 0,
            'avg_response_time': operations.aggregate(
                avg=models.Avg('response_time')
            )['avg'] or 0,
        }

    @classmethod
    def get_module_breakdown(cls, start_date=None, end_date=None):
        """Get cost/usage breakdown by module."""
        queryset = cls.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset.values('module').annotate(
            total_operations=models.Count('id'),
            total_cost=models.Sum('cost'),
            total_tokens=models.Sum('tokens_used'),
            avg_response_time=models.Avg('response_time')
        ).order_by('-total_cost')
