from __future__ import division
from numpy import array, shape, where, in1d
import math
import time
import nose

__author__ = 'zheng'


class InformationTheoryTool:

    def __init__(self, data):
        """
        """
        # Check if all rows have the same length
        assert (len(data.shape) == 2)
        # Save data
        self.data = data
        self.n_rows = data.shape[0]
        self.n_cols = data.shape[1]

    def single_entropy(self, x_index, log_base, debug = False):
        """
        Calculate the entropy of a random variable
        """
        # Check if index are into the bounds
        assert (x_index >= 0 and x_index <= self.n_rows)
        # Variable to return entropy
        summation = 0.0
        # Get uniques values of random variables
        values_x = set(data[x_index])
        # Print debug info
        if debug:
            print 'Entropy of'
            print data[x_index]
        # For each random
        for value_x in values_x:
            px = shape(where(data[x_index] == value_x))[1] / self.n_cols
            if px > 0.0:
                summation += px * math.log(px, log_base)
            if debug:
                print '(%d) px:%f' % (value_x, px)
        if summation == 0.0:
            return summation
        else:
            return - summation


    def entropy(self, x_index, y_index, log_base, debug = False):
        """
        Calculate the entropy between two random variable
        """
        assert (x_index >= 0 and x_index <= self.n_rows)
        assert (y_index >= 0 and y_index <= self.n_rows)
        # Variable to return MI
        summation = 0.0
        # Get uniques values of random variables
        values_x = set(data[x_index])
        values_y = set(data[y_index])
        # Print debug info
        if debug:
            print 'Entropy between'
            print data[x_index]
            print data[y_index]
        # For each random
        for value_x in values_x:
            for value_y in values_y:
                pxy = len(where(in1d(where(data[x_index]==value_x)[0],
                                where(data[y_index]==value_y)[0])==True)[0]) / self.n_cols
                if pxy > 0.0:
                    summation += pxy * math.log(pxy, log_base)
                if debug:
                    print '(%d,%d) pxy:%f' % (value_x, value_y, pxy)
        if summation == 0.0:
            return summation
        else:
            return - summation



    def mutual_information(self, x_index, y_index, log_base, debug = False):
        """
        Calculate and return Mutual information between two random variables
        """
        # Check if index are into the bounds
        assert (x_index >= 0 and x_index <= self.n_rows)
        assert (y_index >= 0 and y_index <= self.n_rows)
        # Variable to return MI
        summation = 0.0
        # Get uniques values of random variables
        values_x = set(data[x_index])
        values_y = set(data[y_index])
        # Print debug info
        if debug:
            print 'MI between'
            print data[x_index]
            print data[y_index]
        # For each random
        for value_x in values_x:
            for value_y in values_y:
                px = shape(where(data[x_index]==value_x))[1] / self.n_cols
                py = shape(where(data[y_index]==value_y))[1] / self.n_cols
                pxy = len(where(in1d(where(data[x_index]==value_x)[0],
                                where(data[y_index]==value_y)[0])==True)[0]) / self.n_cols
                if pxy > 0.0:
                    summation += pxy * math.log((pxy / (px*py)), log_base)
                if debug:
                    print '(%d,%d) px:%f py:%f pxy:%f' % (value_x, value_y, px, py, pxy)
        return summation



# Define data array
data = array( [ (0, 0, 1, 1, 0, 1, 1, 2, 2, 2),
                (3, 4, 5, 5, 3, 2, 2, 6, 6, 1),
                (7, 2, 1, 3, 2, 8, 9, 1, 2, 0),
                (7, 7, 7, 7, 7, 7, 7, 7, 7, 7),
                (0, 1, 2, 3, 4, 5, 6, 7, 1, 1)])
# Create object
it_tool = InformationTheoryTool(data)


# --- Checking single random var entropy

# entropy of  X_1 (3, 4, 5, 5, 3, 2, 2, 6, 6, 1)
t_start = time.time()
print 'Entropy(X_1): %f' % it_tool.single_entropy(1, 10, debug=True)
print 'Elapsed time: %f\n' % (time.time() - t_start)

# entropy of  X_3 (7, 7, 7, 7, 7, 7, 7, 7, 7, 7)
t_start = time.time()
print 'Entropy(X_3): %f' % it_tool.single_entropy(3, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)

# entropy of  X_4 (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
t_start = time.time()
print 'Entropy(X_4): %f' % it_tool.single_entropy(4, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)



# --- Checking entropy between two random variables

# entropy of  X_0 (0, 0, 1, 1, 0, 1, 1, 2, 2, 2) and X_1 (3, 4, 5, 5, 3, 2, 2, 6, 6, 1)
t_start = time.time()
print 'Entropy(X_0, X_1): %f' % it_tool.entropy(0, 1, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)

# entropy of  X_3 (7, 7, 7, 7, 7, 7, 7, 7, 7, 7) and X_3 (7, 7, 7, 7, 7, 7, 7, 7, 7, 7)
t_start = time.time()
print 'Entropy(X_3, X_3): %f' % it_tool.entropy(3, 3, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)



# ---Checking Mutual Information between two random variables

# Print mutual information between X_0 (0,0,1,1,0,1,1,2,2,2) and X_1 (3,4,5,5,3,2,2,6,6,1)
t_start = time.time()
print 'MI(X_0, X_1): %f' % it_tool.mutual_information(0, 1, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)

# Print mutual information between X_1 (3,4,5,5,3,2,2,6,6,1) and X_2 (7,2,1,3,2,8,9,1,2,0)
t_start = time.time()
print 'MI(X_1, X_2): %f' % it_tool.mutual_information(1, 2, 10)
print 'Elapsed time: %f\n' % (time.time() - t_start)



# --- Checking results

# Checking entropy results
for i in range(0,data.shape[0]):
    assert(it_tool.entropy(i, i, 10) == it_tool.single_entropy(i, 10))

# Checking mutual information results
# MI(X,Y) = H(X) + H(Y) - H(X,Y)
n_rows = data.shape[0]
i = 0
while i < n_rows:
    j = i + 1
    while j < n_rows:
        if j != i:
            nose.tools.assert_almost_equal(it_tool.mutual_information(i, j, 10),
                        it_tool.single_entropy(i, 10)+it_tool.single_entropy(j, 10)-it_tool.entropy(i, j, 10))
        j += 1
    i += 1



# This is a stand-alone implementation for Mutual Information
# In probability theory and information theory, the mutual information of two variables
# is a quantity that measures the mutual dependence of the two random variables.
# It is used in Machine Learning (Classification) as a way for feature-selection.

# Author: Tarek Amr <@gr33ndata>

import os, math
from preprocessor import Preprocessor

class MutualInformation:

        def __init__(self, files_path='', classes={}, out_file='output.csv'):
                # self.mi_terms looks like this {'term1': {'d': 3, 't': 4, 'mi': 2, },}
                self.mi_terms = {}
                # self.mi_classes looks like this {'d': 3, 't': 4}
                self.mi_classes = {}
                self.total_terms_count = 0
                # Some configuration
                self.files_path = files_path
                self.out_file = out_file
                self.classes = classes
                self.files_prefixes = classes.keys()
                self.class_names = [classes[prefix] for prefix in classes]
                # For tokenizing, stemming, etc.
                self.prep = Preprocessor(pattern='\W+', lower=True, stem=False, stemmer_name='porter', pos=False, ngram=1)

        # Read terms from files, and fill self.mi_terms & self.mi_classes
        def load_terms(self):
                files = os.listdir(self.files_path)
                for filename in files:
                        #print filename
                        terms = []
                        file_prefix = ''
                        if filename.startswith(self.files_prefixes[0]):
                                file_prefix = self.files_prefixes[0]
                         elif filename.startswith(self.files_prefixes[1]):
                                file_prefix = self.files_prefixes[1]
                        else:
                                continue
                        fd = open('%s/%s' % (self.files_path, filename), 'r')
                        file_data = fd.read()
                        fd.close()
                        terms = self.prep.ngram_tokenizer(text=file_data)
                        for term in terms:
                                self.total_terms_count += 1
                                if not self.mi_terms.has_key(term):
                                        self.mi_terms[term] = {self.files_prefixes[0]: 0, self.files_prefixes[1]: 0}
                                self.mi_terms[term][file_prefix] += 1
                                if self.mi_classes.has_key(file_prefix):
                                        self.mi_classes[file_prefix] += 1
                                else:
                                        self.mi_classes[file_prefix] = 0
                print self.mi_classes

        # Term probablility
        def pr_term(self, term):
                term_count = self.mi_terms[term][self.files_prefixes[0]] + self.mi_terms[term][self.files_prefixes[1]]
                total_count = self.mi_classes[self.files_prefixes[0]] + self.mi_classes[self.files_prefixes[1]]
                return term_count * 1.00 / total_count

        # Class probability
        def pr_class(self, class_prefix):
                class_count = self.mi_classes[class_prefix]
                total_count = self.mi_classes[self.files_prefixes[0]] + self.mi_classes[self.files_prefixes[1]]
                return class_count * 1.00 / total_count

        # Posterior Probability Pr(term/class)
        def pr_post(self, term, class_prefix):
                term_count = self.mi_terms[term][class_prefix]
                total_count = self.mi_classes[class_prefix]
                return term_count * 1.00 / total_count

        # Joint Probability Pr(term, class)
        def pr_joint(self, term, class_prefix):
                return self.pr_post(term, class_prefix) * self.pr_class(class_prefix)

        # Q = 1- P
        def q(self, p):
                return (1 - p)

        # Calculate Mutual Information
        def calculate_mi(self):
                for term in self.mi_terms:
                        mi = 0.0
                        for class_prefix in self.files_prefixes:
                                try:
	                                ### freq(term) > =0, meaning occured
                                        mi += self.pr_joint(term, class_prefix) * math.log10(self.pr_post(term, class_prefix) / self.pr_term(term))
                                    ### freq(term) = 0
                                        mi += self.q(self.pr_joint(term, class_prefix)) * math.log10(self.q(self.pr_post(term, class_prefix)) / self.q(self.pr_term(term)))

                                except:
                                        # Ok, log(0), let's set mi = -1
                                        mi = 0
                        self.mi_terms[term]['mi'] = mi

        # Dump results into a CSV File
        def mi2csv(self):
                fd = open(self.out_file , 'w')
                header_line = "Term, %s, %s, Mutual Info\n" % (self.classes[self.files_prefixes[0]], self.classes[self.files_prefixes[1]])
                fd.write(header_line)
                for term in self.mi_terms:
                        new_line = '%s, %f, %f, %f\n' % (term, self.mi_terms[term][self.files_prefixes[0]],
                                                self.mi_terms[term][self.files_prefixes[1]], self.mi_terms[term]['mi'])
                        fd.write(new_line)
                fd.close()

if __name__ == '__main__':

        # Path to our data files
        my_path = '../all-folds/fold1'

        # We need to tell it which file prefix is tied to which class
        # {'s':'Spam', 'h': 'Ham'} =>
        #         All files staring with s will be considered as Spam dataset
        #        All files staring with h will be considered as Ham dataset
        my_classes = {'a': 'Apple', 'n': 'Nokia'}

        mi = MutualInformation(files_path=my_path, classes=my_classes)
        mi.load_terms()
        mi.calculate_mi()
        mi.mi2csv()