echo "<TestCases>" > testCases.xml
for file in `grep --include=*.py -r "if __name__"| sed 's/ //g'`
do
	echo $file
	test=`echo $file | cut -d':' -f1`
	name=`echo $file | cut -d':' -f2 | cut -c6- | cut -d'(' -f1`
	echo "    <TestCase>" >> testCases.xml
	echo "            <PackageName>GenericFrameworkPackage</PackageName>" >> testCases.xml
	echo "            <TestCaseName>$test</TestCaseName>" >> testCases.xml
	echo "            <Command>python</Command>" >> testCases.xml
	echo "            <Arguments>$test</Arguments>" >> testCases.xml
	echo "            <IsEvent>false</IsEvent>" >> testCases.xml
	echo "    </TestCase>" >> testCases.xml
done
echo "</TestCases>" >> testCases.xml
