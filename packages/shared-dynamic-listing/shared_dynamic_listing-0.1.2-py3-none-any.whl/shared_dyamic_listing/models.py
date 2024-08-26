# from django.db import models
#
#
# class ColumnsTitleOutputModel(models.Model):
#     columnId = models.IntegerField()
#     titleId = models.IntegerField()
#     isTitle = models.BooleanField()
#     columnTitle = models.CharField(max_length=255, null=True, blank=True)
#     columnName = models.CharField(max_length=255, null=True, blank=True)
#     columnStatus = models.CharField(max_length=255, null=True, blank=True)
#     countryId = models.IntegerField()
#     entityId = models.IntegerField()
#     isBusiness = models.BooleanField(null=True, blank=True)
#     hasOption = models.BooleanField(null=True, blank=True)
#     optionId = models.IntegerField(null=True, blank=True)
#     optionName = models.CharField(max_length=255, null=True, blank=True)
#     optionDescription = models.CharField(max_length=255, null=True, blank=True)
#     isAdmin = models.BooleanField(null=True, blank=True)
#     isDeleted = models.BooleanField(null=True, blank=True)
#     isActive = models.BooleanField(null=True, blank=True)
#     isShown = models.BooleanField(null=True, blank=True)
#     isDefault = models.BooleanField(null=True, blank=True)
#     createdBy = models.IntegerField(null=True, blank=True)
#     createdOn = models.DateTimeField(null=True, blank=True)
#     modifiedBy = models.IntegerField(null=True, blank=True)
#     modifiedOn = models.DateTimeField(null=True, blank=True)
#
#
# class ColumnsTitlesOutputModelNew(models.Model):
#     columnTitle = models.CharField(max_length=255, null=True, blank=True)
#     isTitle = models.BooleanField()
#     isDefault = models.BooleanField(null=True, blank=True)
#     isBusiness = models.BooleanField(null=True, blank=True)
#     isAdmin = models.BooleanField(null=True, blank=True)
#     isShown = models.BooleanField(null=True, blank=True)
#     isActive = models.BooleanField(null=True, blank=True)
#
#
# class ListingPreferencesOutPutModel(models.Model):
#     columnId = models.IntegerField(null=True, blank=True)
#     columnName = models.CharField(max_length=255, null=True, blank=True)
#     columnStatus = models.CharField(max_length=255, null=True, blank=True)
#     columnTitle = models.CharField(max_length=255, null=True, blank=True)
#     hasOption = models.BooleanField(null=True, blank=True)
#     entityId = models.IntegerField(null=True, blank=True)
#     position = models.IntegerField(null=True, blank=True)
#     isSticky = models.BooleanField(null=True, blank=True)
#     isShown = models.BooleanField(null=True, blank=True)
#     isAdmin = models.BooleanField(null=True, blank=True)
#     isBusiness = models.BooleanField(null=True, blank=True)
#     isDeleted = models.BooleanField(null=True, blank=True)
#     createdBy = models.IntegerField(null=True, blank=True)
#     createdOn = models.DateTimeField(null=True, blank=True)
#     modifiedBy = models.IntegerField(null=True, blank=True)
#     modifiedOn = models.DateTimeField(null=True, blank=True)
#
#
# class DynamicGenericOutputModel(models.Model):
#     code = models.IntegerField()
#     message = models.CharField(max_length=255, null=True, blank=True)
#
#
# class ListingOptionOutPutModel(models.Model):
#     optionName = models.CharField(max_length=255, null=True, blank=True)
#     optionDescription = models.CharField(max_length=255, null=True, blank=True)
#
#
# class OptionDataOutPutModel(models.Model):
#     optionId = models.IntegerField()
#     optionName = models.CharField(max_length=255, null=True, blank=True)
#     optionDescription = models.CharField(max_length=255, null=True, blank=True)
#
#
# class TitleColumnsOutputModel(models.Model):
#     columnId = models.IntegerField()
#     columnName = models.CharField(max_length=255, null=True, blank=True)
#     columnStatus = models.CharField(max_length=255, null=True, blank=True)
#     hasOption = models.BooleanField()
#     titles = models.ManyToManyField(ColumnsTitlesOutputModelNew, blank=True)
#     options = models.ManyToManyField(OptionDataOutPutModel, blank=True)
#
#
# class ListingPreferencesOutPutModelUpdated(models.Model):
#     columnId = models.IntegerField(null=True, blank=True)
#     columnName = models.CharField(max_length=255, null=True, blank=True)
#     columnStatus = models.CharField(max_length=255, null=True, blank=True)
#     columnTitle = models.CharField(max_length=255, null=True, blank=True)
#     hasOption = models.BooleanField(null=True, blank=True)
#     entityId = models.IntegerField(null=True, blank=True)
#     position = models.IntegerField(null=True, blank=True)
#     isSticky = models.BooleanField(null=True, blank=True)
#     isShown = models.BooleanField(null=True, blank=True)
#     isAdmin = models.BooleanField(null=True, blank=True)
#     isBusiness = models.BooleanField(null=True, blank=True)
#     isDeleted = models.BooleanField(null=True, blank=True)
#     createdBy = models.IntegerField(null=True, blank=True)
#     createdOn = models.DateTimeField(null=True, blank=True)
#     modifiedBy = models.IntegerField(null=True, blank=True)
#     modifiedOn = models.DateTimeField(null=True, blank=True)
#     options = models.ManyToManyField(ListingOptionOutPutModel, blank=True)
#     titles = models.ManyToManyField(ColumnsTitlesOutputModelNew, blank=True)
#
#
# class CountryList(models.Model):
#     countryId = models.AutoField(primary_key=True)
#     columns = models.ManyToManyField(TitleColumnsOutputModel, blank=True)
#
#
# class ColumnsTitleResponseModel(models.Model):
#     businessId = models.IntegerField()
#     country = models.ManyToManyField(CountryList, blank=True)
#
#
# class ColumnsTitleResponseModelNew(DynamicGenericOutputModel):
#     columnsData = models.ManyToManyField(ColumnsTitleResponseModel, blank=True)
#
#
# class ListingPreferencesResponsePutModelNew(DynamicGenericOutputModel):
#     listingPreference = models.ManyToManyField(ListingPreferencesOutPutModelUpdated, blank=True)