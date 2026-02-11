from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Structure, Level

class StructureTreeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create levels
        self.level1 = Level.objects.create(name="Level 1")
        self.level2 = Level.objects.create(name="Level 2")
        
        # Create structures
        # Root
        self.root = Structure.objects.create(name="Root", level=self.level1)
        
        # Child 1
        self.child1 = Structure.objects.create(name="Child 1", structure=self.root, level=self.level2)
        
        # Child 2
        self.child2 = Structure.objects.create(name="Child 2", structure=self.root, level=self.level2)
        
        # Grandchild
        self.grandchild = Structure.objects.create(name="Grandchild", structure=self.child1, level=self.level2)

    def test_get_tree(self):
        url = reverse('structure-tree')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        tree = response.data
        # Should have 1 root node
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['name'], "Root")
        
        # Root should have 2 children
        children = tree[0].get('children', [])
        self.assertEqual(len(children), 2)
        
        # Check for Grandchild
        child1 = next(c for c in children if c['name'] == "Child 1")
        self.assertEqual(len(child1.get('children', [])), 1)
        self.assertEqual(child1['children'][0]['name'], "Grandchild")

    def test_get_children(self):
        url = reverse('structure-get-children', args=[self.root.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all descendants (Child 1, Child 2, Grandchild)
        # The current implementation returns a flat list of all descendants
        data = response.data
        self.assertEqual(len(data), 3)
        names = [item['name'] for item in data]
        self.assertIn("Child 1", names)
        self.assertIn("Child 2", names)
        self.assertIn("Grandchild", names)

    def test_get_parent(self):
        url = reverse('structure-get-parent', args=[self.grandchild.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return path to root: Grandchild -> Child 1 -> Root
        # The implementation returns ancestors.
        data = response.data
        # Based on get_all_parent_structure implementation:
        # parent=[node]
        # while node.structure is not None: ... parent.append(node)
        # return reversed(parent)
        # So it should be [Root, Child 1, Grandchild] or similar depending on inclusion
        
        # Let's check the names
        names = [item['name'] for item in data]
        self.assertIn("Root", names)
        self.assertIn("Child 1", names)
        self.assertIn("Grandchild", names)
