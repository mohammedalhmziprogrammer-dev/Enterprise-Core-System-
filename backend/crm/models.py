from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.basemodel import BaseModel



class Customer(BaseModel):
    """
    Customer = شركة/عميل (Account)
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)  # اختياري
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_customers"
    )

    def __str__(self):
        return self.name


class Contact(BaseModel):
    """
    Contact = شخص داخل العميل (Account Contact)
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    position = models.CharField(max_length=120, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.customer.name})"


class LeadStatus(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    QUALIFIED = "qualified", "Qualified"
    LOST = "lost", "Lost"
    CONVERTED = "converted", "Converted"


class LeadSource(models.TextChoices):
    WEBSITE = "website", "Website"
    REFERRAL = "referral", "Referral"
    ADS = "ads", "Ads"
    CALL = "call", "Call"
    OTHER = "other", "Other"


class Lead(BaseModel):
    """
    Lead = عميل محتمل (قبل التحويل إلى Customer/Opportunity)
    """
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)

    status = models.CharField(max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW)
    source = models.CharField(max_length=20, choices=LeadSource.choices, default=LeadSource.OTHER)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_leads"
    )
    notes = models.TextField(blank=True, null=True)

    # optional: إذا تحوّل إلى Customer
    converted_customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="converted_from_leads"
    )

    def __str__(self):
        return self.full_name


class OpportunityStage(models.TextChoices):
    PROSPECTING = "prospecting", "Prospecting"
    PROPOSAL = "proposal", "Proposal"
    NEGOTIATION = "negotiation", "Negotiation"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class Opportunity(BaseModel):
    """
    Opportunity = صفقة/فرصة بيع
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="opportunities")
    title = models.CharField(max_length=255)

    stage = models.CharField(max_length=20, choices=OpportunityStage.choices, default=OpportunityStage.PROSPECTING)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    expected_close_date = models.DateField(blank=True, null=True)
    probability = models.PositiveSmallIntegerField(default=10)  # 0..100

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_opportunities"
    )
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="opportunities")

    def __str__(self):
        return f"{self.title} - {self.customer.name}"


class ActivityType(models.TextChoices):
    CALL = "call", "Call"
    MEETING = "meeting", "Meeting"
    EMAIL = "email", "Email"
    TASK = "task", "Task"


class ActivityStatus(models.TextChoices):
    OPEN = "open", "Open"
    DONE = "done", "Done"
    CANCELED = "canceled", "Canceled"



class Note(BaseModel):
    content = models.TextField()

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="crm_notes"
    )
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="crm_notes"   # ✅ بدلاً من "notes"
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="crm_notes"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="crm_notes_created"
    )
    def __str__(self):
        return f"Note {self.id} by {self.created_by}"