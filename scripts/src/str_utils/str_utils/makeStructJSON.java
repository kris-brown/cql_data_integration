package str_utils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public final class makeStructJSON {

	public static String run(String ns, String xs, String ys, String zs, Double x0, Double x1, Double x2, Double y0,
			Double y1, Double y2, Double z0, Double z1, Double z2) throws IOException {
		String file = "/Users/ksb/aql_test/scripts/struct_json.py ";

		String cmd = "python3 " + file + String.join(" ", ns, xs, ys, zs, x0.toString(), x1.toString(), x2.toString(),
				y0.toString(), y1.toString(), y2.toString(), z0.toString(), z1.toString(), z2.toString());

		Process process = Runtime.getRuntime().exec(cmd);

		String result = new BufferedReader(new InputStreamReader(process.getInputStream())).lines()
				.collect(Collectors.joining("\n"));
		
		//String err = new BufferedReader(new InputStreamReader(process.getErrorStream())).lines()
		//		.collect(Collectors.joining("\n"));		

		return result;

	}
}
