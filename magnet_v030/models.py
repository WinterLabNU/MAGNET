from django.db import models

# Create your models here.


class Gene(models.Model):

    # stores main gene symbols
    gene_symbol = models.CharField(max_length=50)

    def __str__(self):
        return self.gene_symbol


class Alias(models.Model):

    # stores known gene symbol aliases and ensembl ids of Gene object
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    alias_name = models.CharField(max_length=100)

    def __str__(self):
        return self.gene.gene_symbol + "-" + self.alias_name


class Dataset(models.Model):

    # stores meta info of the datasets, associates with clusters
    # all information except dataset_name are entered in admin interface
    dataset_name = models.CharField(max_length=200, unique=True)
    full_title = models.TextField(blank=True)
    authors = models.TextField(blank=True)
    publication_date = models.DateField(blank=True, null=True)
    journal = models.CharField(max_length=100, blank=True)
    link_to_pubmed = models.URLField(blank=True)
    abstract = models.TextField(blank=True)

    def __str__(self):
        return self.dataset_name


class Cluster(models.Model):

    # child table of Dataset
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cluster_number = models.IntegerField()
    cluster_description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["cluster_number"]

    def __str__(self):
        return self.cluster_description + " (" + str(self.cluster_number) + ")"


class Annotation(models.Model):

    # links a Cluster to a Gene
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)

    def __str__(self):
        return '{} --- {} --- {}'.format(
            str(self.gene),
            str(self.cluster.dataset),
            str(self.cluster)
        )
