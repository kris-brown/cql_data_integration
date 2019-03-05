package str_utils;

import java.util.HashMap;
import java.util.Arrays;
public final class makeCompositionDict {
  /*
   * Convert "H,He,Li,He," ==> "{1:1,2:2,3:1}",  "H,H,H" ==> "{1:3}"
   *
   * i.e. take a comma-separated list of chemical symbols and return a python-like dictionary string
   * 	   which maps atomic number to the number of times that element appeared in the string
   * 	   (dictionary should be sorted)
   */
    public static void main(String[] args) {
        System.out.println(makeCompositionDict.run("H,He,He,Li"));
    }
  private static final HashMap<String, Integer> chem() {
	  HashMap<String, Integer> map = new HashMap<String, Integer>();
    map.put("H", 1);map.put("He", 2);map.put("Li", 3);map.put("Be", 4);map.put("B", 5);map.put("C", 6);map.put("N", 7);map.put("O", 8);map.put("F", 9);map.put("Ne", 10);map.put("Na", 11);map.put("Mg", 12);map.put("Al", 13);map.put("Si", 14);map.put("P", 15);map.put("S", 16);map.put("Cl", 17);map.put("Ar", 18);map.put("K", 19);map.put("Ca", 20);map.put("Sc", 21);map.put("Ti", 22);map.put("V", 23);map.put("Cr", 24);map.put("Mn", 25);map.put("Fe", 26);map.put("Co", 27);map.put("Ni", 28);map.put("Cu", 29);map.put("Zn", 30);map.put("Ga", 31);map.put("Ge", 32);map.put("As", 33);map.put("Se", 34);map.put("Br", 35);map.put("Kr", 36);map.put("Rb", 37);map.put("Sr", 38);map.put("Y", 39);map.put("Zr", 40);map.put("Nb", 41);map.put("Mo", 42);map.put("Tc", 43);map.put("Ru", 44);map.put("Rh", 45);map.put("Pd", 46);map.put("Ag", 47);map.put("Cd", 48);map.put("In", 49);map.put("Sn", 50);map.put("Sb", 51);map.put("Te", 52);map.put("I", 53);map.put("Xe", 54);map.put("Cs", 55);map.put("Ba", 56);map.put("La", 57);map.put("Ce", 58);map.put("Pr", 59);map.put("Nd", 60);map.put("Pm", 61);map.put("Sm", 62);map.put("Eu", 63);map.put("Gd", 64);map.put("Tb", 65);map.put("Dy", 66);map.put("Ho", 67);map.put("Er", 68);map.put("Tm", 69);map.put("Yb", 70);map.put("Lu", 71);map.put("Hf", 72);map.put("Ta", 73);map.put("W", 74);map.put("Re", 75);map.put("Os", 76);map.put("Ir", 77);map.put("Pt", 78);map.put("Au", 79);map.put("Hg", 80);map.put("Tl", 81);map.put("Pb", 82);map.put("Bi", 83);map.put("Po", 84);map.put("At", 85);map.put("Rn", 86);map.put("Fr", 87);map.put("Ra", 88);map.put("Ac", 89);map.put("Th", 90);map.put("Pa", 91);map.put("U", 92);map.put("Np", 93);map.put("Pu", 94);map.put("Am", 95);map.put("Cm", 96);map.put("Bk", 97);map.put("Cf", 98);map.put("Es", 99);
	  return map;
  }

  public static String run(String input) {
  	HashMap<Integer, Integer> map = new HashMap<Integer, Integer>();
  	HashMap<String, Integer> chem = makeCompositionDict.chem();
  	String[] elems = input.split(",");

  	for (int i=0;i<elems.length;i++) {
        String elemSym = elems[i];
        int elemNum  = chem.get(elemSym); // symbol -> atomic number
        map.put(elemNum, map.getOrDefault(elemNum,0)+1); // set to 1 if not found, otherwise increment by 1
      }

  	Integer[] keys = map.keySet().toArray(new Integer[map.size()]);
  	Arrays.sort(keys);

    String out = "";

    for (int i=0;i<keys.length;i++) {
    	out += keys[i].toString() + ':' + map.get(keys[i]).toString();
    	if (i+1 < keys.length) out += ",";
    }
    return '{' + out + '}';
  }
}
