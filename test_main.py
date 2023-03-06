import pandas as pd
import pytest

df = pd.read_csv("res//train_ctrUa4K.csv")


def show_dataframe():
    print(df.head())
    print(df.describe())
    # print(self.df)


def test_gender():
    assert df['Gender'].unique().tolist().sort() == ['Female', 'Male'].sort()


def test_married():
    assert df['Married'].unique().tolist().sort() == ['Yes', 'No'].sort()


def test_income():
    assert (df['ApplicantIncome'] > 0).all() == True


def test_loan_amount_term():
    assert (df['Loan_Amount_Term'] > 600).all() == 0


def test_area():
    assert df['Property_Area'].unique().tolist().sort() == ['Urban', 'Rural', 'Semiurban'].sort()


'''if __name__ == "__main__":
    inst = TestCSV(csv_file_path="res//train_ctrUa4K.csv")
    inst.show_dataframe()'''
