# sEMG Analysis
data <- read.csv("~/Documents/Dissertation/sEMG/Neural-Breakout/Notebooks/testing_data.csv")

head(data)
summary(data)
str(data)
boxplot(data[,-9])

# Preprocessing and data cleaning
table(data['Rect'])
plot(table(data['Rect']), type="l", main="Number of measurements per point on screen", ylab="Number of measurements")

data['Rect'] = data$Rect/max(data$Rect)

# EDA
right = data[data['Rect'] > 0.5,]
left = data[data['Rect'] < 0.5,]

boxplot(left)
boxplot(right)

# Unscaled PCA
pca = prcomp(data, scale = F)
summary(pca)
biplot(pca, cex=0.6, main = "Unscaled PCA") # Cex can be used to reduce textsize
biplot(pca,choices=c(2,3)) # Plots PC2 against PC3
# We can see that the third channel has the most variance. 

# Scaled PCA
pca_s = prcomp(data, scale = T)
# Scale decides if variables should be scaled to have unit
# variance before the analysis takes place. 
summary(pca_s)
pca_s$rotation         # Gives Loadings
pca_s$x                # Gives scores
biplot(pca_s, cex=0.6) # Cex can be used to reduce textsize
biplot(pca_s,choices=c(2,3)) # Plots PC2 against PC3

# Correlations
cor(data)
# If our data correlated
library(heatmap3)
heatmap3(cor(train), symm=T, revC = T, scale="none")
heatmap3(cor(data), scale="none")
heatmap(cor(data))
heatmap3(cor(data), symm=T)

plot.ts(data)

plot.ts(data[c("Rect", "Three")])

data[c("Rect", "Three")]

# Partial Least Squares Regression analysis
library(pls)

# Making our Partial Least Squares model with 10 fold cross validation
plsr_model = plsr(Rect~.,data=data, ncomp = 8, scale = T, validation = "CV")

### Plotting the RMSEP
summary(plsr_model)
# We can select by eye in the plot
plot(RMSEP(plsr_model), legendpos = "topright", type='b', pch=19)

# PLSR with 3 components, and 10 fold cross validation
min_plsr_model = plsr(Rect~.,data=data, ncomp = 3, scale = T, validation = "CV")
summary(min_plsr_model)
